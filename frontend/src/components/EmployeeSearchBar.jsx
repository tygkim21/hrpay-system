import { Input, Select, Button, Space } from 'antd';
import { useState } from 'react';

const { Option } = Select;

/**
 * 직원 목록 검색/필터 바
 *
 * Props:
 *   departments  - 부서 목록 [{id, name}]
 *   onSearch     - (params) => void  { search, department, is_active }
 */
export default function EmployeeSearchBar({ departments = [], onSearch }) {
  const [search,    setSearch]    = useState('');
  const [deptId,    setDeptId]    = useState('');
  const [isActive,  setIsActive]  = useState('');

  const handleSearch = () => {
    const params = {};
    if (search)   params.search     = search;
    if (deptId)   params.department = deptId;
    if (isActive) params.is_active  = isActive;
    onSearch(params);
  };

  const handleReset = () => {
    setSearch('');
    setDeptId('');
    setIsActive('');
    onSearch({});
  };

  return (
    <Space wrap style={{ marginBottom: 16 }}>
      <Input
        placeholder="이름 또는 사번 검색"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        onPressEnter={handleSearch}
        style={{ width: 200 }}
      />

      <Select
        placeholder="부서 선택"
        value={deptId || undefined}
        onChange={setDeptId}
        allowClear
        style={{ width: 160 }}
      >
        {departments.map((d) => (
          <Option key={d.id} value={d.id}>{d.name}</Option>
        ))}
      </Select>

      <Select
        placeholder="재직 상태"
        value={isActive || undefined}
        onChange={setIsActive}
        allowClear
        style={{ width: 120 }}
      >
        <Option value="true">재직</Option>
        <Option value="false">퇴직</Option>
      </Select>

      <Button type="primary" onClick={handleSearch}>검색</Button>
      <Button onClick={handleReset}>초기화</Button>
    </Space>
  );
}
