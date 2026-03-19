import { useState, useEffect, useCallback } from 'react';
import {
  Table, Input, Select, Button, Tag, Space, message, Modal, Form,
  Popover, Tooltip, Card, Row, Col,
} from 'antd';
import {
  SearchOutlined, DownloadOutlined, EditOutlined, TagsOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  getLeads, updateLead, batchUpdateLeads, getAllTags, exportExcel, getLeadStats,
} from '../api/client';

const STATUS_OPTIONS = ['未联系', '已联系', '有意向', '无意向', '已成交', '无效'];

interface Lead {
  id: number;
  name: string;
  phone: string;
  city: string;
  district: string;
  address: string;
  industry: string;
  status: string;
  tags: string[];
  notes: string;
  source: string;
  search_keyword: string;
  created_at: string;
}

export default function Leads() {
  const [data, setData] = useState<Lead[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [filterCity, setFilterCity] = useState<string[]>([]);
  const [filterStatus, setFilterStatus] = useState('');
  const [filterTag, setFilterTag] = useState('');
  const [filterPhone, setFilterPhone] = useState('');
  const [allTags, setAllTags] = useState<string[]>([]);
  const [cities, setCities] = useState<string[]>([]);
  const [selectedRowKeys, setSelectedRowKeys] = useState<number[]>([]);
  const [editModal, setEditModal] = useState(false);
  const [editingLead, setEditingLead] = useState<Lead | null>(null);
  const [form] = Form.useForm();
  const [newTag, setNewTag] = useState('');
  const [batchStatus, setBatchStatus] = useState('');
  const [batchTag, setBatchTag] = useState('');

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string | number> = { page, page_size: pageSize };
      if (search) params.search = search;
      if (filterCity.length) params.city = filterCity.join(',');
      if (filterStatus) params.status = filterStatus;
      if (filterTag) params.tag = filterTag;
      if (filterPhone) params.has_phone = filterPhone;
      const res = await getLeads(params);
      setData(res.data.items);
      setTotal(res.data.total);
    } catch {
      message.error('加载数据失败');
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, search, filterCity, filterStatus, filterTag, filterPhone]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    getAllTags().then((r) => setAllTags(r.data)).catch(() => {});
    getLeadStats().then((r) => {
      setCities(Object.keys(r.data.by_city));
    }).catch(() => {});
  }, []);

  const handleStatusChange = async (id: number, status: string) => {
    try {
      await updateLead(id, { status });
      setData((prev) => prev.map((l) => (l.id === id ? { ...l, status } : l)));
      message.success('状态已更新');
    } catch {
      message.error('更新失败');
    }
  };

  const handleAddTag = async (lead: Lead, tag: string) => {
    if (!tag || lead.tags.includes(tag)) return;
    const newTags = [...lead.tags, tag];
    try {
      await updateLead(lead.id, { tags: newTags });
      setData((prev) => prev.map((l) => (l.id === lead.id ? { ...l, tags: newTags } : l)));
      if (!allTags.includes(tag)) setAllTags([...allTags, tag]);
    } catch {
      message.error('添加标签失败');
    }
  };

  const handleRemoveTag = async (lead: Lead, tag: string) => {
    const newTags = lead.tags.filter((t) => t !== tag);
    try {
      await updateLead(lead.id, { tags: newTags });
      setData((prev) => prev.map((l) => (l.id === lead.id ? { ...l, tags: newTags } : l)));
    } catch {
      message.error('删除标签失败');
    }
  };

  const openEdit = (lead: Lead) => {
    setEditingLead(lead);
    form.setFieldsValue({
      phone: lead.phone,
      address: lead.address,
      notes: lead.notes,
    });
    setEditModal(true);
  };

  const saveEdit = async () => {
    if (!editingLead) return;
    const values = form.getFieldsValue();
    try {
      await updateLead(editingLead.id, values);
      message.success('保存成功');
      setEditModal(false);
      fetchData();
    } catch {
      message.error('保存失败');
    }
  };

  const handleBatchStatus = async () => {
    if (!selectedRowKeys.length || !batchStatus) return;
    try {
      await batchUpdateLeads({ ids: selectedRowKeys, status: batchStatus });
      message.success(`已更新 ${selectedRowKeys.length} 条记录`);
      setSelectedRowKeys([]);
      setBatchStatus('');
      fetchData();
    } catch {
      message.error('批量更新失败');
    }
  };

  const handleBatchTag = async () => {
    if (!selectedRowKeys.length || !batchTag) return;
    try {
      await batchUpdateLeads({ ids: selectedRowKeys, add_tags: [batchTag] });
      message.success(`已为 ${selectedRowKeys.length} 条记录添加标签`);
      setSelectedRowKeys([]);
      setBatchTag('');
      fetchData();
      if (!allTags.includes(batchTag)) setAllTags([...allTags, batchTag]);
    } catch {
      message.error('批量添加标签失败');
    }
  };

  const handleExport = async () => {
    try {
      const params: Record<string, string> = {};
      if (search) params.search = search;
      if (filterCity.length) params.city = filterCity.join(',');
      if (filterStatus) params.status = filterStatus;
      if (filterTag) params.tag = filterTag;
      const res = await exportExcel(params);
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement('a');
      a.href = url;
      a.download = `客户名单_${new Date().toISOString().slice(0, 10)}.xlsx`;
      a.click();
      window.URL.revokeObjectURL(url);
      message.success('导出成功');
    } catch {
      message.error('导出失败');
    }
  };

  const columns: ColumnsType<Lead> = [
    {
      title: '公司名称',
      dataIndex: 'name',
      width: 240,
      ellipsis: true,
    },
    {
      title: '联系电话',
      dataIndex: 'phone',
      width: 160,
      render: (phone: string) =>
        phone ? (
          <span style={{ color: '#c00', fontWeight: 600 }}>{phone}</span>
        ) : (
          <span style={{ color: '#ccc' }}>-</span>
        ),
    },
    {
      title: '城市',
      dataIndex: 'city',
      width: 80,
    },
    {
      title: '区县',
      dataIndex: 'district',
      width: 80,
    },
    {
      title: '行业',
      dataIndex: 'industry',
      width: 140,
      ellipsis: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 120,
      render: (status: string, record: Lead) => (
        <Select
          size="small"
          value={status}
          style={{ width: 100 }}
          onChange={(v) => handleStatusChange(record.id, v)}
          options={STATUS_OPTIONS.map((s) => ({ label: s, value: s }))}
          popupMatchSelectWidth={false}
        />
      ),
    },
    {
      title: '标签',
      dataIndex: 'tags',
      width: 200,
      render: (tags: string[], record: Lead) => (
        <Space size={4} wrap>
          {tags.map((tag) => (
            <Tag key={tag} closable onClose={() => handleRemoveTag(record, tag)} color="blue">
              {tag}
            </Tag>
          ))}
          <Popover
            trigger="click"
            content={
              <Space.Compact>
                <Input
                  size="small"
                  placeholder="新标签"
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onPressEnter={() => {
                    handleAddTag(record, newTag);
                    setNewTag('');
                  }}
                  style={{ width: 100 }}
                />
                <Button
                  size="small"
                  type="primary"
                  onClick={() => {
                    handleAddTag(record, newTag);
                    setNewTag('');
                  }}
                >
                  添加
                </Button>
              </Space.Compact>
            }
          >
            <Tag style={{ cursor: 'pointer', borderStyle: 'dashed' }}>
              <TagsOutlined /> 添加
            </Tag>
          </Popover>
        </Space>
      ),
    },
    {
      title: '操作',
      width: 80,
      render: (_: unknown, record: Lead) => (
        <Tooltip title="编辑">
          <Button type="link" icon={<EditOutlined />} onClick={() => openEdit(record)} />
        </Tooltip>
      ),
    },
  ];

  return (
    <div>
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={[12, 12]}>
          <Col span={5}>
            <Input
              placeholder="搜索公司名/电话/地址"
              prefix={<SearchOutlined />}
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              allowClear
            />
          </Col>
          <Col span={5}>
            <Select
              mode="multiple"
              style={{ width: '100%' }}
              placeholder="城市（多选）"
              value={filterCity}
              onChange={(v) => { setFilterCity(v); setPage(1); }}
              allowClear
              showSearch
              maxTagCount="responsive"
              options={cities.map((c) => ({ label: c, value: c }))}
            />
          </Col>
          <Col span={4}>
            <Select
              style={{ width: '100%' }}
              placeholder="状态"
              value={filterStatus || undefined}
              onChange={(v) => { setFilterStatus(v || ''); setPage(1); }}
              allowClear
              options={STATUS_OPTIONS.map((s) => ({ label: s, value: s }))}
            />
          </Col>
          <Col span={4}>
            <Select
              style={{ width: '100%' }}
              placeholder="标签"
              value={filterTag || undefined}
              onChange={(v) => { setFilterTag(v || ''); setPage(1); }}
              allowClear
              options={allTags.map((t) => ({ label: t, value: t }))}
            />
          </Col>
          <Col span={3}>
            <Select
              style={{ width: '100%' }}
              placeholder="电话"
              value={filterPhone || undefined}
              onChange={(v) => { setFilterPhone(v || ''); setPage(1); }}
              allowClear
              options={[
                { label: '有电话', value: 'yes' },
                { label: '无电话', value: 'no' },
              ]}
            />
          </Col>
          <Col span={3}>
            <Button icon={<DownloadOutlined />} onClick={handleExport}>
              导出 Excel
            </Button>
          </Col>
        </Row>
      </Card>

      {selectedRowKeys.length > 0 && (
        <Card size="small" style={{ marginBottom: 16 }}>
          <Space>
            <span>已选 {selectedRowKeys.length} 条</span>
            <Select
              size="small"
              placeholder="批量改状态"
              value={batchStatus || undefined}
              onChange={setBatchStatus}
              style={{ width: 120 }}
              options={STATUS_OPTIONS.map((s) => ({ label: s, value: s }))}
            />
            <Button size="small" type="primary" onClick={handleBatchStatus} disabled={!batchStatus}>
              应用
            </Button>
            <Input
              size="small"
              placeholder="批量加标签"
              value={batchTag}
              onChange={(e) => setBatchTag(e.target.value)}
              style={{ width: 120 }}
            />
            <Button size="small" type="primary" onClick={handleBatchTag} disabled={!batchTag}>
              添加
            </Button>
            <Button size="small" onClick={() => setSelectedRowKeys([])}>
              取消选择
            </Button>
          </Space>
        </Card>
      )}

      <Table
        rowKey="id"
        columns={columns}
        dataSource={data}
        loading={loading}
        size="middle"
        scroll={{ x: 1200 }}
        rowSelection={{
          selectedRowKeys,
          onChange: (keys) => setSelectedRowKeys(keys as number[]),
        }}
        pagination={{
          current: page,
          pageSize,
          total,
          showSizeChanger: true,
          showTotal: (t) => `共 ${t} 条`,
          onChange: (p, ps) => { setPage(p); setPageSize(ps); },
        }}
      />

      <Modal
        title={`编辑 - ${editingLead?.name}`}
        open={editModal}
        onOk={saveEdit}
        onCancel={() => setEditModal(false)}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item label="联系电话" name="phone">
            <Input />
          </Form.Item>
          <Form.Item label="详细地址" name="address">
            <Input />
          </Form.Item>
          <Form.Item label="备注" name="notes">
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
