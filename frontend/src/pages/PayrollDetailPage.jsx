import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Card, Descriptions, Typography, Button, Divider, Space, Spin } from 'antd';

import { getPayroll } from '../api/payrollApi';
import PayrollStatusBadge from '../components/PayrollStatusBadge';

const { Title } = Typography;

const fmt = (v) => Number(v).toLocaleString('ko-KR') + '원';

export default function PayrollDetailPage() {
  const { id }     = useParams();
  const navigate   = useNavigate();

  const { data: record, isLoading } = useQuery({
    queryKey: ['payroll', id],
    queryFn:  () => getPayroll(id),
    select:   (res) => res.data.data,
  });

  if (isLoading) return <Spin style={{ margin: 40 }} />;
  if (!record)   return <div style={{ padding: 24 }}>급여 정보를 찾을 수 없습니다.</div>;

  return (
    <div style={{ padding: 24, maxWidth: 700 }}>
      <Space style={{ marginBottom: 16 }}>
        <Button onClick={() => navigate(-1)}>← 뒤로</Button>
      </Space>

      <Title level={4}>
        급여 명세서 — {record.employee_name} ({record.year}년 {record.month}월)
        {'  '}
        <PayrollStatusBadge status={record.status} label={record.status_display} />
      </Title>

      <Card title="지급 항목" style={{ marginBottom: 16 }}>
        <Descriptions column={1} bordered size="small">
          <Descriptions.Item label="기본급">{fmt(record.base_salary)}</Descriptions.Item>
          <Descriptions.Item label="식대">{fmt(record.meal_allowance)}</Descriptions.Item>
          <Descriptions.Item label="교통비">{fmt(record.transport_allowance)}</Descriptions.Item>
          <Descriptions.Item label="초과근무수당">
            {fmt(record.overtime_pay)} (초과근무 {record.overtime_minutes}분)
          </Descriptions.Item>
          <Descriptions.Item label="총 지급액">
            <strong>{fmt(record.gross_pay)}</strong>
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="공제 항목" style={{ marginBottom: 16 }}>
        <Descriptions column={1} bordered size="small">
          <Descriptions.Item label="국민연금">{fmt(record.national_pension)}</Descriptions.Item>
          <Descriptions.Item label="건강보험">{fmt(record.health_insurance)}</Descriptions.Item>
          <Descriptions.Item label="장기요양보험">{fmt(record.long_term_care)}</Descriptions.Item>
          <Descriptions.Item label="고용보험">{fmt(record.employment_insurance)}</Descriptions.Item>
          <Descriptions.Item label="소득세">{fmt(record.income_tax)}</Descriptions.Item>
          <Descriptions.Item label="지방소득세">{fmt(record.local_income_tax)}</Descriptions.Item>
          <Descriptions.Item label="총 공제액">
            <strong>{fmt(record.total_deduction)}</strong>
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <Card>
        <Descriptions column={1} bordered>
          <Descriptions.Item label="실 수령액">
            <Title level={4} style={{ margin: 0, color: '#1677ff' }}>{fmt(record.net_pay)}</Title>
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {record.confirmed_at && (
        <div style={{ marginTop: 16, color: '#888' }}>
          확정일시: {new Date(record.confirmed_at).toLocaleString('ko-KR')}
        </div>
      )}
    </div>
  );
}
