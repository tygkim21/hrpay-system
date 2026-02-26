import { Tag } from 'antd';

const COLOR_MAP = {
  PENDING:  'blue',
  APPROVED: 'green',
  REJECTED: 'red',
};

export default function LeaveStatusBadge({ status, label }) {
  return <Tag color={COLOR_MAP[status] ?? 'default'}>{label ?? status}</Tag>;
}
