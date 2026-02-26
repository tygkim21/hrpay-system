import { useQuery } from '@tanstack/react-query';
import { Table, Typography } from 'antd';
import { useNavigate } from 'react-router-dom';

import { getMyPayrolls } from '../api/payrollApi';
import PayrollStatusBadge from '../components/PayrollStatusBadge';

const { Title } = Typography;

const fmt = (v) => Number(v).toLocaleString('ko-KR') + '원';

export default function MyPayrollPage() {
  const navigate = useNavigate();

  const { data: records = [], isLoading } = useQuery({
    queryKey: ['my-payrolls'],
    queryFn:  getMyPayrolls,
    select:   (res) => res.data.data,
  });

  const columns = [
    { title: '연도', dataIndex: 'year',  key: 'year' },
    { title: '월',   dataIndex: 'month', key: 'month', render: (v) => `${v}월` },
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
      title: '명세서',
      key: 'detail',
      render: (_, row) => (
        <a onClick={() => navigate(`/payroll/${row.id}`)}>보기</a>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Title level={3}>내 급여 내역</Title>
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
