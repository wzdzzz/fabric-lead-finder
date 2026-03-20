import { useState, useEffect } from 'react';
import {
  Card, Table, Button, Modal, Form, Input, InputNumber, Tag, Space,
  message, Progress, Popconfirm, Typography, Grid,
} from 'antd';
import {
  PlusOutlined, DeleteOutlined, SwapOutlined, KeyOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { getAmapKeys, addAmapKey, activateAmapKey, deleteAmapKey } from '../api/client';

const { Title } = Typography;
const { useBreakpoint } = Grid;

interface AmapKey {
  id: number;
  key: string;
  name: string;
  is_active: boolean;
  monthly_limit: number;
  used_count: number;
  reset_month: string;
  created_at: string;
}

export default function AmapKeys() {
  const [keys, setKeys] = useState<AmapKey[]>([]);
  const [loading, setLoading] = useState(false);
  const [addModal, setAddModal] = useState(false);
  const [form] = Form.useForm();
  const screens = useBreakpoint();
  const isMobile = !screens.md;

  const fetchKeys = async () => {
    setLoading(true);
    try {
      const res = await getAmapKeys();
      setKeys(res.data);
    } catch {
      message.error('加载 Key 列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchKeys(); }, []);

  const handleAdd = async () => {
    try {
      const values = await form.validateFields();
      await addAmapKey(values);
      message.success('添加成功');
      setAddModal(false);
      form.resetFields();
      fetchKeys();
    } catch {
      message.error('添加失败');
    }
  };

  const handleActivate = async (id: number) => {
    try {
      await activateAmapKey(id);
      message.success('已切换');
      fetchKeys();
    } catch {
      message.error('切换失败');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteAmapKey(id);
      message.success('已删除');
      fetchKeys();
    } catch {
      message.error('删除失败');
    }
  };

  const maskKey = (key: string) => {
    if (key.length <= 8) return key;
    return key.slice(0, 4) + '****' + key.slice(-4);
  };

  const columns: ColumnsType<AmapKey> = [
    {
      title: '名称', dataIndex: 'name', width: 120,
      render: (name: string, record: AmapKey) => (
        <Space>
          <span>{name}</span>
          {record.is_active && <Tag color="green">当前</Tag>}
        </Space>
      ),
    },
    {
      title: 'Key', dataIndex: 'key', width: 200,
      render: (key: string) => <code>{maskKey(key)}</code>,
    },
    {
      title: '用量', width: 250,
      render: (_: unknown, record: AmapKey) => {
        const percent = record.monthly_limit > 0
          ? Math.round((record.used_count / record.monthly_limit) * 100) : 0;
        const status = percent >= 100 ? 'exception' : percent >= 80 ? 'active' : 'normal';
        return (
          <div>
            <Progress percent={percent} size="small" status={status} />
            <span style={{ fontSize: 12, color: '#999' }}>
              {record.used_count} / {record.monthly_limit}
            </span>
          </div>
        );
      },
    },
    {
      title: '重置月份', dataIndex: 'reset_month', width: 100,
    },
    {
      title: '操作', width: 160,
      render: (_: unknown, record: AmapKey) => (
        <Space>
          {!record.is_active && (
            <Button
              type="link" size="small" icon={<SwapOutlined />}
              onClick={() => handleActivate(record.id)}
            >
              切换
            </Button>
          )}
          <Popconfirm title="确认删除？" onConfirm={() => handleDelete(record.id)}>
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 移动端卡片模式
  if (isMobile) {
    return (
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <Title level={4} style={{ margin: 0 }}>高德 Key 管理</Title>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setAddModal(true)}>
            添加
          </Button>
        </div>

        {keys.map((record) => {
          const percent = record.monthly_limit > 0
            ? Math.round((record.used_count / record.monthly_limit) * 100) : 0;
          const status = percent >= 100 ? 'exception' as const : percent >= 80 ? 'active' as const : 'normal' as const;
          return (
            <Card key={record.id} size="small" style={{ marginBottom: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <Space>
                  <KeyOutlined />
                  <span style={{ fontWeight: 600 }}>{record.name}</span>
                  {record.is_active && <Tag color="green">当前</Tag>}
                </Space>
              </div>
              <div style={{ marginBottom: 8 }}>
                <code style={{ fontSize: 12, color: '#666' }}>{maskKey(record.key)}</code>
              </div>
              <Progress percent={percent} size="small" status={status} />
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 8 }}>
                <span style={{ fontSize: 12, color: '#999' }}>
                  {record.used_count} / {record.monthly_limit} ({record.reset_month})
                </span>
                <Space>
                  {!record.is_active && (
                    <Button type="link" size="small" onClick={() => handleActivate(record.id)}>切换</Button>
                  )}
                  <Popconfirm title="确认删除？" onConfirm={() => handleDelete(record.id)}>
                    <Button type="link" size="small" danger>删除</Button>
                  </Popconfirm>
                </Space>
              </div>
            </Card>
          );
        })}

        {!loading && keys.length === 0 && (
          <Card><div style={{ textAlign: 'center', color: '#999' }}>暂无 Key，请添加</div></Card>
        )}

        <Modal
          title="添加高德 Key"
          open={addModal}
          onOk={handleAdd}
          onCancel={() => { setAddModal(false); form.resetFields(); }}
          okText="添加"
          cancelText="取消"
          width="95%"
        >
          <Form form={form} layout="vertical">
            <Form.Item label="Key" name="key" rules={[{ required: true, message: '请输入 Key' }]}>
              <Input placeholder="高德地图 API Key" />
            </Form.Item>
            <Form.Item label="备注名称" name="name">
              <Input placeholder="如：主号、备用号" />
            </Form.Item>
            <Form.Item label="每月额度" name="monthly_limit" initialValue={5000}>
              <InputNumber min={1} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item label="已用次数" name="used_count" initialValue={0}>
              <InputNumber min={0} style={{ width: '100%' }} placeholder="非必填，默认为 0" />
            </Form.Item>
          </Form>
        </Modal>
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>高德 Key 管理</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setAddModal(true)}>
          添加 Key
        </Button>
      </div>

      <Table
        rowKey="id"
        columns={columns}
        dataSource={keys}
        loading={loading}
        size="middle"
        pagination={false}
      />

      <Modal
        title="添加高德 Key"
        open={addModal}
        onOk={handleAdd}
        onCancel={() => { setAddModal(false); form.resetFields(); }}
        okText="添加"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item label="Key" name="key" rules={[{ required: true, message: '请输入 Key' }]}>
            <Input placeholder="高德地图 API Key" />
          </Form.Item>
          <Form.Item label="备注名称" name="name">
            <Input placeholder="如：主号、备用号" />
          </Form.Item>
          <Form.Item label="每月额度" name="monthly_limit" initialValue={5000}>
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
