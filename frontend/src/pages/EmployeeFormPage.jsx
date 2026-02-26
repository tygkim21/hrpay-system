import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Form, Input, Select, Button, Typography,
  Space, InputNumber, message, Spin,
} from 'antd';

import {
  getEmployee, createEmployee, updateEmployee,
  getDepartments, getPositions,
} from '../api/employeeApi';

const { Title } = Typography;
const { Option } = Select;

export default function EmployeeFormPage() {
  const { id }      = useParams();          // id 없으면 신규 등록
  const isEdit      = Boolean(id);
  const navigate    = useNavigate();
  const queryClient = useQueryClient();
  const [form]      = Form.useForm();

  // 기존 직원 데이터 (수정 시)
  const { data: employee, isLoading: empLoading } = useQuery({
    queryKey: ['employee', id],
    queryFn:  () => getEmployee(id),
    select:   (res) => res.data.data,
    enabled:  isEdit,
  });

  // 부서/직급 목록
  const { data: departments } = useQuery({
    queryKey: ['departments'],
    queryFn:  getDepartments,
    select:   (res) => res.data.data,
  });

  const { data: positions } = useQuery({
    queryKey: ['positions'],
    queryFn:  getPositions,
    select:   (res) => res.data.data,
  });

  // 수정 시 폼 초기값 세팅
  useEffect(() => {
    if (isEdit && employee) {
      form.setFieldsValue({
        employee_no: employee.employee_no,
        name:        employee.name,
        department:  employee.department?.id,
        position:    employee.position?.id,
        hire_date:   employee.hire_date,
        base_salary: Number(employee.base_salary),
        // 주민번호: 마스킹 상태로 표시 (수정 시 재입력 가능)
        resident_no: '',
      });
    }
  }, [employee, isEdit, form]);

  const mutation = useMutation({
    mutationFn: (values) =>
      isEdit
        ? updateEmployee(id, values)
        : createEmployee(values),
    onSuccess: (res) => {
      message.success(res.data.message || '저장되었습니다.');
      queryClient.invalidateQueries({ queryKey: ['employees'] });
      if (isEdit) {
        queryClient.invalidateQueries({ queryKey: ['employee', id] });
        navigate(`/employees/${id}`);
      } else {
        navigate('/employees');
      }
    },
    onError: (err) => {
      const msg = err.response?.data?.message;
      message.error(typeof msg === 'string' ? msg : '저장 중 오류가 발생했습니다.');
    },
  });

  const handleSubmit = (values) => {
    // 빈 주민번호는 전송하지 않음 (수정 시 변경하지 않으려는 경우)
    if (!values.resident_no) delete values.resident_no;
    mutation.mutate(values);
  };

  if (isEdit && empLoading) return <Spin style={{ display: 'block', marginTop: 80 }} />;

  return (
    <div style={{ padding: 24, maxWidth: 640 }}>
      <Space style={{ marginBottom: 16 }}>
        <Button onClick={() => navigate(isEdit ? `/employees/${id}` : '/employees')}>
          ← 취소
        </Button>
        <Title level={3} style={{ margin: 0 }}>
          {isEdit ? '직원 정보 수정' : '직원 등록'}
        </Title>
      </Space>

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
      >
        <Form.Item
          label="사번"
          name="employee_no"
          rules={[{ required: true, message: '사번을 입력해주세요.' }]}
        >
          <Input placeholder="예: EMP2024001" disabled={isEdit} />
        </Form.Item>

        <Form.Item
          label="이름"
          name="name"
          rules={[{ required: true, message: '이름을 입력해주세요.' }]}
        >
          <Input placeholder="홍길동" />
        </Form.Item>

        <Form.Item
          label="주민등록번호"
          name="resident_no"
          rules={[{
            pattern: /^[0-9]{6}-[0-9]{7}$/,
            message: '형식: YYMMDD-NNNNNNN',
          }]}
          extra={
            isEdit
              ? `변경하지 않으려면 비워두세요. ${employee?.resident_no ? '(현재 등록된 번호 있음)' : ''}`
              : ''
          }
        >
          <Input placeholder="990101-1234567" maxLength={14} />
        </Form.Item>

        <Form.Item
          label="부서"
          name="department"
          rules={[{ required: true, message: '부서를 선택해주세요.' }]}
        >
          <Select placeholder="부서 선택">
            {(departments ?? []).map((d) => (
              <Option key={d.id} value={d.id}>{d.name}</Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          label="직급"
          name="position"
          rules={[{ required: true, message: '직급을 선택해주세요.' }]}
        >
          <Select placeholder="직급 선택">
            {(positions ?? []).sort((a, b) => a.level - b.level).map((p) => (
              <Option key={p.id} value={p.id}>{p.name} (Lv.{p.level})</Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          label="입사일"
          name="hire_date"
          rules={[{ required: true, message: '입사일을 입력해주세요.' }]}
        >
          <Input type="date" />
        </Form.Item>

        <Form.Item
          label="기본급 (원)"
          name="base_salary"
          rules={[
            { required: true, message: '기본급을 입력해주세요.' },
            { type: 'number', min: 1, message: '기본급은 0보다 커야 합니다.' },
          ]}
        >
          <InputNumber
            style={{ width: '100%' }}
            formatter={(v) => `${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
            parser={(v) => v.replace(/,/g, '')}
            placeholder="예: 3000000"
          />
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={mutation.isPending}
            block
          >
            {isEdit ? '수정 저장' : '직원 등록'}
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
}
