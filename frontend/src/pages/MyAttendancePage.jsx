import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Table, Select, Typography, Space, Button, message, Popconfirm } from 'antd';

import { getLeaves, approveLeave } from '../api/attendanceApi';
import LeaveStatusBadge from '../components/LeaveStatusBadge';

const { Title } = Typography;
const { Option } = Select;

/**
 * HR/ADMIN 전용: 전체 직원 휴가 신청 목록 + 승인/반려 처리
 */
export default function MyAttendancePage() {
  const [filter, setFilter] = useState('ALL');
  const queryClient = useQueryClient();

  const { data: leaves = [], isLoading } = useQuery({
    queryKey: ['leaves'],
    queryFn:  () => getLeaves(),
    select:   (res) => res.data.data,
  });

  const approveMutation = useMutation({
    mutationFn: ({ id, action, reject_reason }) =>
      approveLeave(id, { action, reject_reason }),
    onSuccess: (res) => {
      message.success(res.data.message || '처리되었습니다.');
      queryClient.invalidateQueries({ queryKey: ['leaves'] });
    },
    onError: (err) => {
      const msg = err.response?.data?.message;
      message.error(typeof msg === 'string' ? msg : '처리 중 오류가 발생했습니다.');
    },
  });

  const filtered = filter === 'ALL'
    ? leaves
    : leaves.filter((l) => l.status === filter);

  const columns = [
    { title: '직원명', dataIndex: 'employee_name', key: 'employee_name' },
    { title: '종류',   dataIndex: 'leave_type_display', key: 'leave_type_display' },
    { title: '시작일', dataIndex: 'start_date', key: 'start_date' },
    { title: '종료일', dataIndex: 'end_date', key: 'end_date' },
    { title: '사유',   dataIndex: 'reason', key: 'reason', ellipsis: true },
    {
      title: '상태',
      dataIndex: 'status',
      key: 'status',
      render: (v, row) => <LeaveStatusBadge status={v} label={row.status_display} />,
    },
    {
      title: '처리',
      key: 'action',
      render: (_, row) => row.status !== 'PENDING' ? null : (
        <Space>
          <Popconfirm
            title="승인하시겠습니까?"
            onConfirm={() => approveMutation.mutate({ id: row.id, action: 'approve' })}
            okText="승인"
            cancelText="취소"
          >
            <Button size="small" type="primary">승인</Button>
          </Popconfirm>
          <Popconfirm
            title="반려 사유를 입력하세요. (확인 클릭 시 '사유 없음'으로 반려됩니다)"
            onConfirm={() => approveMutation.mutate({ id: row.id, action: 'reject', reject_reason: '반려' })}
            okText="반려"
            cancelText="취소"
            okButtonProps={{ danger: true }}
          >
            <Button size="small" danger>반려</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Title level={3}>휴가 관리</Title>

      <Space style={{ marginBottom: 16 }}>
        <Select value={filter} onChange={setFilter} style={{ width: 120 }}>
          <Option value="ALL">전체</Option>
          <Option value="PENDING">신청</Option>
          <Option value="APPROVED">승인</Option>
          <Option value="REJECTED">반려</Option>
        </Select>
      </Space>

      <Table
        columns={columns}
        dataSource={filtered}
        rowKey="id"
        loading={isLoading}
        size="small"
        locale={{ emptyText: '휴가 신청 내역이 없습니다.' }}
      />
    </div>
  );
}
