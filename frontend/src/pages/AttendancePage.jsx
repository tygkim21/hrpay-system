import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Button, Space, Typography, Select, message, Card } from 'antd';

import { checkIn, checkOut, getMonthlyAttendance } from '../api/attendanceApi';
import MonthlyCalendar from '../components/MonthlyCalendar';

const { Title } = Typography;
const { Option } = Select;

const now = new Date();

export default function AttendancePage() {
  const [year,  setYear]  = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const queryClient = useQueryClient();

  const { data: records = [], isLoading } = useQuery({
    queryKey: ['attendance-monthly', year, month],
    queryFn:  () => getMonthlyAttendance(year, month),
    select:   (res) => res.data.data,
  });

  const checkInMutation = useMutation({
    mutationFn: checkIn,
    onSuccess: (res) => {
      message.success(res.data.message || '출근 처리되었습니다.');
      queryClient.invalidateQueries({ queryKey: ['attendance-monthly'] });
    },
    onError: (err) => {
      const msg = err.response?.data?.message;
      message.error(typeof msg === 'string' ? msg : '출근 처리 중 오류가 발생했습니다.');
    },
  });

  const checkOutMutation = useMutation({
    mutationFn: checkOut,
    onSuccess: (res) => {
      message.success(res.data.message || '퇴근 처리되었습니다.');
      queryClient.invalidateQueries({ queryKey: ['attendance-monthly'] });
    },
    onError: (err) => {
      const msg = err.response?.data?.message;
      message.error(typeof msg === 'string' ? msg : '퇴근 처리 중 오류가 발생했습니다.');
    },
  });

  const years  = [now.getFullYear() - 1, now.getFullYear()];
  const months = Array.from({ length: 12 }, (_, i) => i + 1);

  return (
    <div style={{ padding: 24 }}>
      <Title level={3}>출퇴근 관리</Title>

      <Card style={{ marginBottom: 24, maxWidth: 400 }}>
        <Space>
          <Button
            type="primary"
            onClick={() => checkInMutation.mutate()}
            loading={checkInMutation.isPending}
          >
            출근
          </Button>
          <Button
            danger
            onClick={() => checkOutMutation.mutate()}
            loading={checkOutMutation.isPending}
          >
            퇴근
          </Button>
        </Space>
      </Card>

      <Space style={{ marginBottom: 16 }}>
        <Select value={year} onChange={setYear} style={{ width: 100 }}>
          {years.map((y) => <Option key={y} value={y}>{y}년</Option>)}
        </Select>
        <Select value={month} onChange={setMonth} style={{ width: 80 }}>
          {months.map((m) => <Option key={m} value={m}>{m}월</Option>)}
        </Select>
      </Space>

      <MonthlyCalendar records={records} year={year} month={month} isLoading={isLoading} />
    </div>
  );
}
