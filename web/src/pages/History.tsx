import { useState, useEffect } from 'react';
import { Table, Tag, Typography, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { getTasks } from '../api/client';

const { Title } = Typography;

interface Task {
  id: number;
  keywords: string[];
  regions: string[];
  status: string;
  total_found: number;
  new_added: number;
  progress: number;
  total_steps: number;
  started_at: string | null;
  finished_at: string | null;
  error_msg: string;
}

const STATUS_MAP: Record<string, { color: string; text: string }> = {
  pending: { color: 'default', text: '等待中' },
  running: { color: 'processing', text: '运行中' },
  completed: { color: 'success', text: '已完成' },
  failed: { color: 'error', text: '失败' },
};

export default function History() {
  const [data, setData] = useState<Task[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, [page]);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await getTasks(page, 20);
      setData(res.data.items);
      setTotal(res.data.total);
    } catch {
      message.error('加载任务历史失败');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (t: string | null) => {
    if (!t) return '-';
    return new Date(t).toLocaleString('zh-CN');
  };

  const columns: ColumnsType<Task> = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 60,
    },
    {
      title: '关键词',
      dataIndex: 'keywords',
      render: (kws: string[]) => kws.join(', '),
      ellipsis: true,
    },
    {
      title: '地区',
      dataIndex: 'regions',
      render: (rs: string[]) => rs.join(', '),
      ellipsis: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (s: string) => {
        const info = STATUS_MAP[s] || { color: 'default', text: s };
        return <Tag color={info.color}>{info.text}</Tag>;
      },
    },
    {
      title: '进度',
      width: 100,
      render: (_: unknown, r: Task) => `${r.progress}/${r.total_steps}`,
    },
    {
      title: '找到',
      dataIndex: 'total_found',
      width: 80,
    },
    {
      title: '新增',
      dataIndex: 'new_added',
      width: 80,
    },
    {
      title: '开始时间',
      dataIndex: 'started_at',
      width: 170,
      render: formatTime,
    },
    {
      title: '结束时间',
      dataIndex: 'finished_at',
      width: 170,
      render: formatTime,
    },
  ];

  return (
    <div>
      <Title level={4}>任务历史</Title>
      <Table
        rowKey="id"
        columns={columns}
        dataSource={data}
        loading={loading}
        size="middle"
        pagination={{
          current: page,
          pageSize: 20,
          total,
          onChange: setPage,
          showTotal: (t) => `共 ${t} 条`,
        }}
      />
    </div>
  );
}
