import { useMemo } from 'react';
import { Table, Tag } from 'antd';

/**
 * 월별 근태 기록을 테이블 형태로 표시
 * records: AttendanceRecord[]
 */
export default function MonthlyCalendar({ records = [], year, month }) {
  const columns = [
    {
      title: '근무일',
      dataIndex: 'work_date',
      key: 'work_date',
      width: 120,
    },
    {
      title: '출근',
      dataIndex: 'check_in',
      key: 'check_in',
      render: (v) => v ? new Date(v).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }) : '-',
    },
    {
      title: '퇴근',
      dataIndex: 'check_out',
      key: 'check_out',
      render: (v) => v ? new Date(v).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }) : '-',
    },
    {
      title: '실근무',
      dataIndex: 'work_minutes',
      key: 'work_minutes',
      render: (v) => v ? `${Math.floor(v / 60)}h ${v % 60}m` : '-',
    },
    {
      title: '초과근무',
      dataIndex: 'overtime_minutes',
      key: 'overtime_minutes',
      render: (v) => v > 0
        ? <Tag color="orange">{Math.floor(v / 60)}h {v % 60}m</Tag>
        : '-',
    },
  ];

  const title = useMemo(() => `${year}년 ${month}월 근태 현황`, [year, month]);

  return (
    <Table
      title={() => title}
      columns={columns}
      dataSource={records}
      rowKey="id"
      size="small"
      pagination={false}
      locale={{ emptyText: '근태 기록이 없습니다.' }}
    />
  );
}
