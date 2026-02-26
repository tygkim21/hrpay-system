import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Form, Input, Select, Button, Typography, Space, message } from 'antd';

import { requestLeave } from '../api/attendanceApi';

const { Title } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const LEAVE_TYPES = [
  { value: 'ANNUAL',  label: '연차' },
  { value: 'HALF',    label: '반차' },
  { value: 'SICK',    label: '병가' },
  { value: 'SPECIAL', label: '특별휴가' },
];

export default function LeaveRequestPage() {
  const navigate    = useNavigate();
  const queryClient = useQueryClient();
  const [form]      = Form.useForm();

  const mutation = useMutation({
    mutationFn: (values) => requestLeave(values),
    onSuccess: (res) => {
      message.success(res.data.message || '휴가 신청이 완료되었습니다.');
      queryClient.invalidateQueries({ queryKey: ['leaves'] });
      navigate('/leaves');
    },
    onError: (err) => {
      const msg = err.response?.data?.message;
      message.error(typeof msg === 'string' ? msg : '신청 중 오류가 발생했습니다.');
    },
  });

  return (
    <div style={{ padding: 24, maxWidth: 560 }}>
      <Space style={{ marginBottom: 16 }}>
        <Button onClick={() => navigate('/leaves')}>← 취소</Button>
        <Title level={3} style={{ margin: 0 }}>휴가 신청</Title>
      </Space>

      <Form form={form} layout="vertical" onFinish={(v) => mutation.mutate(v)}>
        <Form.Item
          label="휴가 종류"
          name="leave_type"
          rules={[{ required: true, message: '휴가 종류를 선택해주세요.' }]}
        >
          <Select placeholder="선택">
            {LEAVE_TYPES.map((t) => (
              <Option key={t.value} value={t.value}>{t.label}</Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          label="시작일"
          name="start_date"
          rules={[{ required: true, message: '시작일을 입력해주세요.' }]}
        >
          <Input type="date" />
        </Form.Item>

        <Form.Item
          label="종료일"
          name="end_date"
          rules={[{ required: true, message: '종료일을 입력해주세요.' }]}
        >
          <Input type="date" />
        </Form.Item>

        <Form.Item label="사유" name="reason">
          <TextArea rows={3} placeholder="사유를 입력해주세요." />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" loading={mutation.isPending} block>
            신청하기
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
}
