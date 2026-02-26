import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Descriptions, Button, Space, Modal, Input,
  Typography, message, Spin, Tag,
} from 'antd';

import { getEmployee, resignEmployee } from '../api/employeeApi';
import EmployeeStatusBadge from '../components/EmployeeStatusBadge';

const { Title } = Typography;

export default function EmployeeDetailPage() {
  const { id }         = useParams();
  const navigate       = useNavigate();
  const queryClient    = useQueryClient();
  const [resignOpen,   setResignOpen]   = useState(false);
  const [resignDate,   setResignDate]   = useState('');

  const { data: employee, isLoading } = useQuery({
    queryKey: ['employee', id],
    queryFn:  () => getEmployee(id),
    select:   (res) => res.data.data,
    onError:  () => message.error('직원 정보 조회에 실패했습니다.'),
  });

  const resignMutation = useMutation({
    mutationFn: () => resignEmployee(id, { resign_date: resignDate }),
    onSuccess: (res) => {
      message.success(res.data.message || '퇴직 처리가 완료되었습니다.');
      queryClient.invalidateQueries({ queryKey: ['employee', id] });
      queryClient.invalidateQueries({ queryKey: ['employees'] });
      setResignOpen(false);
    },
    onError: (err) => {
      message.error(err.response?.data?.message || '퇴직 처리 중 오류가 발생했습니다.');
    },
  });

  if (isLoading) return <Spin style={{ display: 'block', marginTop: 80 }} />;
  if (!employee)  return <div style={{ padding: 24 }}>직원 정보를 찾을 수 없습니다.</div>;

  return (
    <div style={{ padding: 24 }}>
      <Space style={{ width: '100%', justifyContent: 'space-between', marginBottom: 16 }}>
        <Space>
          <Button onClick={() => navigate('/employees')}>← 목록</Button>
          <Title level={3} style={{ margin: 0 }}>
            {employee.name}&nbsp;
            <EmployeeStatusBadge isActive={employee.is_active} />
          </Title>
        </Space>
        <Space>
          <Button onClick={() => navigate(`/employees/${id}/edit`)}>수정</Button>
          {employee.is_active && (
            <Button danger onClick={() => setResignOpen(true)}>퇴직 처리</Button>
          )}
        </Space>
      </Space>

      <Descriptions bordered column={2} size="middle">
        <Descriptions.Item label="사번">{employee.employee_no}</Descriptions.Item>
        <Descriptions.Item label="이름">{employee.name}</Descriptions.Item>
        <Descriptions.Item label="부서">{employee.department?.name}</Descriptions.Item>
        <Descriptions.Item label="직급">{employee.position?.name} (Lv.{employee.position?.level})</Descriptions.Item>
        <Descriptions.Item label="입사일">{employee.hire_date}</Descriptions.Item>
        <Descriptions.Item label="퇴사일">{employee.resign_date ?? '-'}</Descriptions.Item>
        <Descriptions.Item label="기본급">
          {Number(employee.base_salary).toLocaleString()}원
        </Descriptions.Item>
        <Descriptions.Item label="주민번호">{employee.resident_no || '-'}</Descriptions.Item>
        <Descriptions.Item label="등록일">{employee.created_at?.slice(0, 10)}</Descriptions.Item>
        <Descriptions.Item label="최종 수정">{employee.updated_at?.slice(0, 10)}</Descriptions.Item>
      </Descriptions>

      {/* 퇴직 처리 모달 */}
      <Modal
        title="퇴직 처리"
        open={resignOpen}
        onCancel={() => setResignOpen(false)}
        onOk={() => resignMutation.mutate()}
        okText="퇴직 처리"
        okButtonProps={{ danger: true, loading: resignMutation.isPending }}
        cancelText="취소"
      >
        <p>{employee.name} 직원을 퇴직 처리합니다.</p>
        <Input
          type="date"
          value={resignDate}
          onChange={(e) => setResignDate(e.target.value)}
          placeholder="퇴직일 (YYYY-MM-DD)"
        />
      </Modal>
    </div>
  );
}
