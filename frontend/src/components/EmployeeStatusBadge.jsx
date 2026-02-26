import { Tag } from 'antd';

/**
 * 재직/퇴직 상태 뱃지
 * @param {boolean} isActive - true: 재직, false: 퇴직
 */
export default function EmployeeStatusBadge({ isActive }) {
  return isActive
    ? <Tag color="green">재직</Tag>
    : <Tag color="red">퇴직</Tag>;
}
