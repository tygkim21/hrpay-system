import { useRef, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useReactToPrint } from 'react-to-print';
import {
  Button, Select, Space, Table, Typography, Descriptions, message,
} from 'antd';

import { getPayrollLedger } from '../api/payrollApi';

const { Title, Text } = Typography;
const { Option } = Select;

const now = new Date();

// ── 프린트 CSS (A4 가로, 한글 폰트, 표 꽉 채움) ─────────────────────
const PAGE_STYLE = `
  @page {
    size: A4 landscape;
    margin: 8mm 10mm;
  }
  body {
    font-size: 8px !important;
    font-family: 'Malgun Gothic', '맑은 고딕', Arial, sans-serif;
  }
  .ant-table-wrapper,
  .ant-table-container,
  .ant-table-content,
  .ant-table-body {
    overflow: visible !important;
  }
  table {
    table-layout: auto !important;
    width: 100% !important;
  }
  th, td {
    font-size: 7.5px !important;
    padding: 1px 3px !important;
    white-space: nowrap;
  }
  .ledger-section-title {
    font-size: 10px !important;
    font-weight: bold;
    margin: 6px 0 2px;
  }
  .ledger-grand-total {
    font-size: 9px !important;
  }
`;

// ── 숫자 포맷 (천단위 콤마) ──────────────────────────────────────────
const fmt = (v) => (v != null ? Number(v).toLocaleString('ko-KR') : '0');

// ── 테이블 컬럼 정의 ─────────────────────────────────────────────────
const COLUMNS = [
  { title: '사번',   dataIndex: 'employee_no',          key: 'employee_no',          width: 80 },
  { title: '이름',   dataIndex: 'employee_name',         key: 'employee_name',         width: 65 },
  { title: '직급',   dataIndex: 'position_name',         key: 'position_name',         width: 55 },
  { title: '기본급', dataIndex: 'base_salary',           key: 'base_salary',           width: 90, align: 'right', render: fmt },
  { title: '식대',   dataIndex: 'meal_allowance',        key: 'meal_allowance',        width: 75, align: 'right', render: fmt },
  { title: '교통비', dataIndex: 'transport_allowance',   key: 'transport_allowance',   width: 75, align: 'right', render: fmt },
  { title: '초과수당', dataIndex: 'overtime_pay',        key: 'overtime_pay',          width: 75, align: 'right', render: fmt },
  {
    title: '총지급액',
    dataIndex: 'gross_pay',
    key: 'gross_pay',
    width: 95,
    align: 'right',
    render: fmt,
    onHeaderCell: () => ({ style: { background: '#dbeafe', fontWeight: 'bold' } }),
    onCell:       () => ({ style: { fontWeight: 'bold' } }),
  },
  { title: '국민연금', dataIndex: 'national_pension',    key: 'national_pension',      width: 78, align: 'right', render: fmt },
  { title: '건강보험', dataIndex: 'health_insurance',    key: 'health_insurance',      width: 78, align: 'right', render: fmt },
  { title: '장기요양', dataIndex: 'long_term_care',      key: 'long_term_care',        width: 78, align: 'right', render: fmt },
  { title: '고용보험', dataIndex: 'employment_insurance', key: 'employment_insurance', width: 78, align: 'right', render: fmt },
  { title: '소득세',  dataIndex: 'income_tax',           key: 'income_tax',            width: 72, align: 'right', render: fmt },
  { title: '지방세',  dataIndex: 'local_income_tax',     key: 'local_income_tax',      width: 72, align: 'right', render: fmt },
  {
    title: '총공제액',
    dataIndex: 'total_deduction',
    key: 'total_deduction',
    width: 92,
    align: 'right',
    render: fmt,
    onHeaderCell: () => ({ style: { background: '#fef3c7', fontWeight: 'bold' } }),
    onCell:       () => ({ style: { fontWeight: 'bold' } }),
  },
  {
    title: '실수령액',
    dataIndex: 'net_pay',
    key: 'net_pay',
    width: 95,
    align: 'right',
    render: fmt,
    onHeaderCell: () => ({ style: { background: '#dcfce7', fontWeight: 'bold' } }),
    onCell:       () => ({ style: { fontWeight: 'bold', color: '#16a34a' } }),
  },
];

// ── 부서별 테이블 컴포넌트 ────────────────────────────────────────────
function DeptTable({ dept }) {
  return (
    <div style={{ marginBottom: 20, breakInside: 'avoid' }}>
      <div className="ledger-section-title" style={{ fontWeight: 'bold', marginBottom: 4, fontSize: 13 }}>
        {dept.name} — {dept.count}명
      </div>
      <Table
        columns={COLUMNS}
        dataSource={dept.records}
        rowKey="id"
        pagination={false}
        size="small"
        scroll={{ x: 'max-content' }}
        summary={() => (
          <Table.Summary.Row style={{ background: '#f5f5f5' }}>
            <Table.Summary.Cell index={0} colSpan={3}>
              <strong>부서 합계</strong>
            </Table.Summary.Cell>
            {/* 기본급~초과수당 (col 3~6): 빈 칸 */}
            {[3, 4, 5, 6].map((i) => (
              <Table.Summary.Cell key={i} index={i} />
            ))}
            {/* 총지급액 (col 7) */}
            <Table.Summary.Cell index={7} align="right">
              <strong>{fmt(dept.subtotal_gross_pay)}</strong>
            </Table.Summary.Cell>
            {/* 국민연금~지방세 (col 8~13): 빈 칸 */}
            {[8, 9, 10, 11, 12, 13].map((i) => (
              <Table.Summary.Cell key={i} index={i} />
            ))}
            {/* 총공제액 (col 14) */}
            <Table.Summary.Cell index={14} align="right">
              <strong>{fmt(dept.subtotal_deduction)}</strong>
            </Table.Summary.Cell>
            {/* 실수령액 (col 15) */}
            <Table.Summary.Cell index={15} align="right">
              <strong style={{ color: '#16a34a' }}>{fmt(dept.subtotal_net_pay)}</strong>
            </Table.Summary.Cell>
          </Table.Summary.Row>
        )}
      />
    </div>
  );
}

// ── 메인 페이지 ──────────────────────────────────────────────────────
export default function PayrollLedgerPage() {
  const printRef = useRef(null);
  const [year,   setYear]   = useState(now.getFullYear());
  const [month,  setMonth]  = useState(now.getMonth() + 1);
  const [params, setParams] = useState({ year: now.getFullYear(), month: now.getMonth() + 1 });

  const { data: ledger, isLoading, isFetching } = useQuery({
    queryKey: ['payroll-ledger', params.year, params.month],
    queryFn:  () => getPayrollLedger(params),
    select:   (res) => res.data.data,
    onError:  () => message.error('급여대장 조회에 실패했습니다.'),
  });

  const handlePrint = useReactToPrint({
    contentRef:    printRef,
    documentTitle: `급여대장_${params.year}년_${params.month}월`,
    pageStyle:     PAGE_STYLE,
  });

  const years  = [now.getFullYear() - 1, now.getFullYear()];
  const months = Array.from({ length: 12 }, (_, i) => i + 1);

  const hasDepts = ledger && ledger.departments.length > 0;

  return (
    <div style={{ padding: 24 }}>
      <Title level={3}>급여대장</Title>

      {/* 검색 조건 — 프린트 시 이 영역은 contentRef 바깥이라 제외됨 */}
      <Space style={{ marginBottom: 24 }} wrap>
        <Select value={year} onChange={setYear} style={{ width: 100 }}>
          {years.map((y) => <Option key={y} value={y}>{y}년</Option>)}
        </Select>
        <Select value={month} onChange={setMonth} style={{ width: 80 }}>
          {months.map((m) => <Option key={m} value={m}>{m}월</Option>)}
        </Select>
        <Button
          type="primary"
          onClick={() => setParams({ year, month })}
          loading={isFetching}
        >
          조회
        </Button>
        <Button
          onClick={handlePrint}
          disabled={!hasDepts}
          title={!hasDepts ? '급여 데이터가 없습니다' : ''}
        >
          PDF 출력
        </Button>
      </Space>

      {/* ── 프린트 대상 영역 ── */}
      <div ref={printRef}>
        {isLoading && (
          <div style={{ padding: 40, textAlign: 'center', color: '#999' }}>조회 중...</div>
        )}

        {ledger && (
          <>
            {/* 문서 헤더 */}
            <div style={{ textAlign: 'center', marginBottom: 16 }}>
              <Title level={4} style={{ margin: 0 }}>급 여 대 장</Title>
              <Text type="secondary">
                {ledger.year}년 {ledger.month}월
                {'　'}출력일: {new Date(ledger.generated_at).toLocaleDateString('ko-KR')}
              </Text>
            </div>

            {/* 요약 */}
            <Descriptions
              bordered
              size="small"
              column={4}
              style={{ marginBottom: 20 }}
            >
              <Descriptions.Item label="총 인원">
                {ledger.total_count}명
              </Descriptions.Item>
              <Descriptions.Item label="총 지급액">
                {fmt(ledger.total_gross_pay)}원
              </Descriptions.Item>
              <Descriptions.Item label="총 공제액">
                {fmt(ledger.total_deduction)}원
              </Descriptions.Item>
              <Descriptions.Item label="총 실수령액">
                <strong style={{ color: '#1677ff' }}>
                  {fmt(ledger.total_net_pay)}원
                </strong>
              </Descriptions.Item>
            </Descriptions>

            {/* 부서별 테이블 */}
            {!hasDepts ? (
              <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                해당 월의 급여 데이터가 없습니다.
              </div>
            ) : (
              ledger.departments.map((dept) => (
                <DeptTable key={dept.name} dept={dept} />
              ))
            )}

            {/* 전체 합계 (부서가 2개 이상일 때만 표시) */}
            {hasDepts && ledger.departments.length > 1 && (
              <div
                className="ledger-grand-total"
                style={{
                  marginTop: 8,
                  padding: '8px 16px',
                  background: '#f0f0f0',
                  borderRadius: 4,
                  display: 'flex',
                  gap: 32,
                  flexWrap: 'wrap',
                }}
              >
                <span><strong>전체 합계 ({ledger.total_count}명)</strong></span>
                <span>총지급액: <strong>{fmt(ledger.total_gross_pay)}원</strong></span>
                <span>총공제액: <strong>{fmt(ledger.total_deduction)}원</strong></span>
                <span>
                  총실수령액:{' '}
                  <strong style={{ color: '#1677ff' }}>{fmt(ledger.total_net_pay)}원</strong>
                </span>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
