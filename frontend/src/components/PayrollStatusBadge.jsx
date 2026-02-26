import { Tag } from 'antd';

const COLOR_MAP = {
  DRAFT:     'blue',
  CONFIRMED: 'green',
};

export default function PayrollStatusBadge({ status, label }) {
  return <Tag color={COLOR_MAP[status] ?? 'default'}>{label ?? status}</Tag>;
}
