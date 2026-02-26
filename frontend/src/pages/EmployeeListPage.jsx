import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Button, Typography, Space, message } from 'antd';
import { useNavigate } from 'react-router-dom';

import { getEmployees, getDepartments } from '../api/employeeApi';
import EmployeeTable     from '../components/EmployeeTable';
import EmployeeSearchBar from '../components/EmployeeSearchBar';

const { Title } = Typography;

export default function EmployeeListPage() {
  const navigate = useNavigate();
  const [queryParams, setQueryParams] = useState({});

  const { data: empRes, isLoading: empLoading } = useQuery({
    queryKey: ['employees', queryParams],
    queryFn:  () => getEmployees(queryParams),
    select:   (res) => res.data.data,
    onError:  () => message.error('직원 목록 조회에 실패했습니다.'),
  });

  const { data: deptRes } = useQuery({
    queryKey: ['departments'],
    queryFn:  getDepartments,
    select:   (res) => res.data.data,
    onError:  () => message.error('부서 목록 조회에 실패했습니다.'),
  });

  return (
    <div style={{ padding: 24 }}>
      <Space style={{ width: '100%', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>직원 관리</Title>
        <Button type="primary" onClick={() => navigate('/employees/new')}>
          직원 등록
        </Button>
      </Space>

      <EmployeeSearchBar
        departments={deptRes ?? []}
        onSearch={setQueryParams}
      />

      <EmployeeTable
        data={empRes ?? []}
        loading={empLoading}
      />
    </div>
  );
}
