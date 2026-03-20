import { useState, useEffect } from 'react';
import { Table, Tag, Typography, message, Grid, Card, Space } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { getTasks } from '../api/client';

const { Title } = Typography;
const { useBreakpoint } = Grid;

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
  const screens = useBreakpoint();
  const isMobile = !screens.md;

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

  const desktopColumns: ColumnsType<Task> = [
    { title: 'ID', dataIndex: 'id', width: 60 },
    { title: '关键词', dataIndex: 'keywords', render: (kws: string[]) => kws.join(', '), ellipsis: true },
    { title: '地区', dataIndex: 'regions', render: (rs: string[]) => rs.join(', '), ellipsis: true },
    {
      title: '状态', dataIndex: 'status', width: 100,
      render: (s: string) => {
        const info = STATUS_MAP[s] || { color: 'default', text: s };
        return <Tag color={info.color}>{info.text}</Tag>;
      },
    },
    { title: '进度', width: 100, render: (_: unknown, r: Task) => `${r.progress}/${r.total_steps}` },
    { title: '找到', dataIndex: 'total_found', width: 80 },
    { title: '新增', dataIndex: 'new_added', width: 80 },
    { title: '开始时间', dataIndex: 'started_at', width: 170, render: formatTime },
    { title: '结束时间', dataIndex: 'finished_at', width: 170, render: formatTime },
  ];

  // 移动端用卡片列表
  if (isMobile) {
    return (
      <div>
        <Title level={4}>任务历史</Title>
        {loading && <Card loading />}
        {data.map((task) => {
          const statusInfo = STATUS_MAP[task.status] || { color: 'default', text: task.status };
          return (
            <Card key={task.id} size="small" style={{ marginBottom: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ fontWeight: 600 }}>任务 #{task.id}</span>
                <Tag color={statusInfo.color}>{statusInfo.text}</Tag>
              </div>
              <div style={{ fontSize: 13, color: '#666' }}>
                <div style={{ marginBottom: 4 }}>关键词: {task.keywords.join(', ')}</div>
                <div style={{ marginBottom: 4 }}>地区: {task.regions.slice(0, 5).join(', ')}{task.regions.length > 5 ? ` 等${task.regions.length}个` : ''}</div>
                <Space size={16}>
                  <span>进度: {task.progress}/{task.total_steps}</span>
                  <span>找到: {task.total_found}</span>
                  <span>新增: {task.new_added}</span>
                </Space>
                {task.started_at && (
                  <div style={{ marginTop: 4, color: '#999', fontSize: 12 }}>
                    {formatTime(task.started_at)}
                  </div>
                )}
              </div>
            </Card>
          );
        })}
        {!loading && data.length === 0 && (
          <Card><div style={{ textAlign: 'center', color: '#999' }}>暂无任务记录</div></Card>
        )}
      </div>
    );
  }

  return (
    <div>
      <Title level={4}>任务历史</Title>
      <Table
        rowKey="id"
        columns={desktopColumns}
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
