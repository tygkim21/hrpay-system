import { Table } from 'antd';
import { useNavigate } from 'react-router-dom';
import EmployeeStatusBadge from './EmployeeStatusBadge';

/**
 * 직원 목록 테이블
 *
 * Props:
 *   data      - 직원 배열
 *   loading   - 로딩 여부
 */
export default function EmployeeTable({ data = [], loading = false }) {
  const navigate = useNavigate();

  const columns = [
    {
      title:     '사번',
      dataIndex: 'employee_no',
      key:       'employee_no',
      width:     100,
    },
    {
      title:     '이름',
      dataIndex: 'name',
      key:       'name',
      width:     100,
    },
    {
      title:  '부서',
      key:    'department',
      render: (_, record) => record.department?.name ?? '-',
      width:  120,
    },
    {
      title:  '직급',
      key:    'position',
      render: (_, record) => record.position?.name ?? '-',
      width:  100,
    },
    {
      title:     '입사일',
      dataIndex: 'hire_date',
      key:       'hire_date',
      width:     110,
    },
    {
      title:  '상태',
      key:    'is_active',
      render: (_, record) => <EmployeeStatusBadge isActive={record.is_active} />,
      width:  80,
    },
  ];

  return (
    <Table
      rowKey="id"
      columns={columns}
      dataSource={data}
      loading={loading}
      pagination={{ pageSize: 20, showSizeChanger: false }}
      onRow={(record) => ({
        onClick: () => navigate(`/employees/${record.id}`),
        style:   { cursor: 'pointer' },
      })}
    />
  );
}
