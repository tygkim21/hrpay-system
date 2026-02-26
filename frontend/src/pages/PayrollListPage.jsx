import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Table, Select, Typography, Space, Button, InputNumber, message, Popconfirm } from 'antd';
import { useNavigate } from 'react-router-dom';

import { getPayrolls, calculatePayroll, confirmPayroll } from '../api/payrollApi';
import { getEmployees } from '../api/employeeApi';
import PayrollStatusBadge from '../components/PayrollStatusBadge';

const { Title } = Typography;
const { Option } = Select;

const now = new Date();

export default function PayrollListPage() {
  const navigate      = useNavigate();
  const queryClient   = useQueryClient();
  const [year,  setYear]       = useState(now.getFullYear());
  const [month, setMonth]      = useState(now.getMonth() + 1);
  const [calcEmpId, setCalcEmpId] = useState(null);

  const { data: records = [], isLoading } = useQuery({
    queryKey: ['payrolls', year, month],
    queryFn:  () => getPayrolls({ year, month }),
    select:   (res) => res.data.data,
  });

  const { data: employees = [] } = useQuery({
    queryKey: ['employees-all'],
    queryFn:  () => getEmployees({ is_active: true }),
    select:   (res) => res.data.data ?? [],
  });

  const calcMutation = useMutation({
    mutationFn: (data) => calculatePayroll(data),
    onSuccess: (res) => {
      message.success(res.data.message || '급여가 계산되었습니다.');
      queryClient.invalidateQueries({ queryKey: ['payrolls'] });
    },
    onError: (err) => {
      const msg = err.response?.data?.message;
      message.error(typeof msg === 'string' ? msg : '급여 계산 중 오류가 발생했습니다.');
    },
  });

  const confirmMutation = useMutation({
    mutationFn: (id) => confirmPayroll(id),
    onSuccess: (res) => {
      message.success(res.data.message || '급여가 확정되었습니다.');
      queryClient.invalidateQueries({ queryKey: ['payrolls'] });
    },
    onError: (err) => {
      const msg = err.response?.data?.message;
      message.error(typeof msg === 'string' ? msg : '급여 확정 중 오류가 발생했습니다.');
    },
  });

  const handleCalculate = () => {
    if (!calcEmpId) {
      message.warning('직원을 선택해주세요.');
      return;
    }
    calcMutation.mutate({ employee_id: calcEmpId, year, month });
  };

  const fmt = (v) => Number(v).toLocaleString('ko-KR') + '원';

  const columns = [
    { title: '직원명',   dataIndex: 'employee_name',   key: 'employee_name' },
    { title: '부서',     dataIndex: 'department_name', key: 'department_name' },
    { title: '총지급액', dataIndex: 'gross_pay',       key: 'gross_pay', render: fmt },
    { title: '총공제액', dataIndex: 'total_deduction', key: 'total_deduction', render: fmt },
    { title: '실수령액', dataIndex: 'net_pay',         key: 'net_pay', render: fmt },
    {
      title: '상태',
      dataIndex: 'status',
      key: 'status',
      render: (v, row) => <PayrollStatusBadge status={v} label={row.status_display} />,
    },
    {
      title: '작업',
      key: 'actions',
      render: (_, row) => (
        <Space>
          <Button size="small" onClick={() => navigate(`/payroll/${row.id}`)}>상세</Button>
          {row.status === 'DRAFT' && (
            <Popconfirm
              title="급여를 확정하시겠습니까?"
              onConfirm={() => confirmMutation.mutate(row.id)}
              okText="확정"
              cancelText="취소"
            >
              <Button size="small" type="primary">확정</Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  const years  = [now.getFullYear() - 1, now.getFullYear()];
  const months = Array.from({ length: 12 }, (_, i) => i + 1);

  return (
    <div style={{ padding: 24 }}>
      <Title level={3}>급여 관리</Title>

      <Space style={{ marginBottom: 16 }} wrap>
        <Select value={year} onChange={setYear} style={{ width: 100 }}>
          {years.map((y) => <Option key={y} value={y}>{y}년</Option>)}
        </Select>
        <Select value={month} onChange={setMonth} style={{ width: 80 }}>
          {months.map((m) => <Option key={m} value={m}>{m}월</Option>)}
        </Select>
      </Space>

      <Space style={{ marginBottom: 16 }} wrap>
        <Select
          placeholder="직원 선택"
          style={{ width: 200 }}
          onChange={setCalcEmpId}
          value={calcEmpId}
          showSearch
          optionFilterProp="children"
        >
          {employees.map((e) => (
            <Option key={e.id} value={e.id}>{e.name} ({e.employee_no})</Option>
          ))}
        </Select>
        <Button
          type="primary"
          onClick={handleCalculate}
          loading={calcMutation.isPending}
        >
          급여 계산
        </Button>
      </Space>

      <Table
        columns={columns}
        dataSource={records}
        rowKey="id"
        loading={isLoading}
        size="small"
        locale={{ emptyText: '급여 내역이 없습니다.' }}
      />
    </div>
  );
}
