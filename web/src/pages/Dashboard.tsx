import { useState, useEffect, useRef } from 'react';
import {
  Card, Row, Col, Statistic, Select, Button, Progress, message, Tag, Space, Typography,
} from 'antd';
import {
  TeamOutlined, PhoneOutlined, SearchOutlined, RocketOutlined,
} from '@ant-design/icons';
import { getKeywords, getRegions, getLeadStats, createTask, getTask } from '../api/client';

const { Title } = Typography;

const REGION_GROUPS: Record<string, string[]> = {
  '广东': ['广州', '东莞', '深圳', '佛山', '中山', '惠州', '汕头', '揭阳', '潮州', '江门', '肇庆', '清远'],
  '浙江': ['杭州', '宁波', '温州', '湖州', '嘉兴', '绍兴', '金华', '义乌', '台州', '丽水', '衢州'],
  '江苏': ['苏州', '南通', '无锡', '常州', '南京', '扬州', '徐州', '盐城', '泰州', '镇江'],
  '福建': ['泉州', '厦门', '莆田', '福州', '漳州', '龙岩', '三明'],
  '山东': ['青岛', '烟台', '济南', '潍坊', '临沂', '淄博', '威海', '济宁', '德州'],
  '河南': ['郑州', '新乡', '商丘', '南阳', '安阳', '洛阳', '许昌', '周口'],
  '湖北': ['武汉', '荆州', '襄阳', '黄石', '孝感', '宜昌'],
  '湖南': ['株洲', '长沙', '湘潭', '常德', '岳阳', '衡阳'],
  '江西': ['南昌', '赣州', '九江', '吉安', '上饶'],
  '辽宁': ['大连', '沈阳', '葫芦岛', '丹东', '营口'],
  '河北': ['石家庄', '保定', '沧州', '邢台', '廊坊', '衡水'],
  '安徽': ['合肥', '芜湖', '阜阳', '安庆', '蚌埠', '宿州'],
  '四川': ['成都', '绵阳', '德阳', '南充', '泸州'],
  '广西': ['南宁', '柳州', '桂林', '玉林'],
  '直辖市': ['上海', '北京', '重庆', '天津'],
  '其他': ['西安', '昆明', '贵阳', '太原', '兰州', '哈尔滨', '长春', '乌鲁木齐', '呼和浩特', '海口'],
};

interface Stats {
  total: number;
  with_phone: number;
  without_phone: number;
  by_status: Record<string, number>;
  by_city: Record<string, number>;
}

interface TaskInfo {
  id: number;
  status: string;
  progress: number;
  total_steps: number;
  total_found: number;
  new_added: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [allKeywords, setAllKeywords] = useState<string[]>([]);
  const [allRegions, setAllRegions] = useState<string[]>([]);
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([]);
  const [selectedRegions, setSelectedRegions] = useState<string[]>([]);
  const [runningTask, setRunningTask] = useState<TaskInfo | null>(null);
  const [launching, setLaunching] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    loadData();
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  const loadData = async () => {
    try {
      const [kwRes, rgRes, stRes] = await Promise.all([
        getKeywords(), getRegions(), getLeadStats(),
      ]);
      setAllKeywords(kwRes.data.keywords);
      setAllRegions(rgRes.data.regions);
      setStats(stRes.data);
    } catch {
      message.error('加载数据失败');
    }
  };

  const selectProvince = (cities: string[]) => {
    setSelectedRegions((prev) => {
      const set = new Set(prev);
      const allSelected = cities.every((c) => set.has(c));
      if (allSelected) {
        cities.forEach((c) => set.delete(c));
      } else {
        cities.forEach((c) => set.add(c));
      }
      return [...set];
    });
  };

  const startScrape = async () => {
    if (!selectedKeywords.length || !selectedRegions.length) {
      message.warning('请选择关键词和地区');
      return;
    }
    setLaunching(true);
    try {
      const res = await createTask(selectedKeywords, selectedRegions);
      const task = res.data as TaskInfo;
      setRunningTask(task);
      message.success(`任务 #${task.id} 已启动`);

      // 轮询进度
      pollRef.current = setInterval(async () => {
        try {
          const r = await getTask(task.id);
          const t = r.data as TaskInfo;
          setRunningTask(t);
          if (t.status === 'completed' || t.status === 'failed') {
            if (pollRef.current) clearInterval(pollRef.current);
            pollRef.current = null;
            if (t.status === 'completed') {
              message.success(`任务完成！找到 ${t.total_found} 条，新增 ${t.new_added} 条`);
            } else {
              message.error('任务失败');
            }
            loadData();
          }
        } catch {
          // ignore poll errors
        }
      }, 2000);
    } catch {
      message.error('启动任务失败');
    } finally {
      setLaunching(false);
    }
  };

  return (
    <div>
      <Title level={4}>数据概览</Title>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic title="客户总数" value={stats?.total ?? 0} prefix={<TeamOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="有联系电话"
              value={stats?.with_phone ?? 0}
              prefix={<PhoneOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="无联系电话" value={stats?.without_phone ?? 0} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="电话覆盖率"
              value={stats?.total ? ((stats.with_phone / stats.total) * 100).toFixed(1) : 0}
              suffix="%"
            />
          </Card>
        </Col>
      </Row>

      <Card title="发起爬取" style={{ marginBottom: 24 }}>
        <div style={{ marginBottom: 16 }}>
          <div style={{ marginBottom: 8, fontWeight: 500 }}>关键词</div>
          <Select
            mode="multiple"
            style={{ width: '100%' }}
            placeholder="选择关键词"
            value={selectedKeywords}
            onChange={setSelectedKeywords}
            options={allKeywords.map((k) => ({ label: k, value: k }))}
          />
        </div>

        <div style={{ marginBottom: 16 }}>
          <div style={{ marginBottom: 8, fontWeight: 500 }}>目标地区</div>
          <div style={{ marginBottom: 8 }}>
            <Space wrap>
              {Object.entries(REGION_GROUPS).map(([province, cities]) => {
                const allSelected = cities.every((c) => selectedRegions.includes(c));
                return (
                  <Tag
                    key={province}
                    color={allSelected ? 'blue' : undefined}
                    style={{ cursor: 'pointer' }}
                    onClick={() => selectProvince(cities)}
                  >
                    {province}
                  </Tag>
                );
              })}
              <Tag
                color={selectedRegions.length === allRegions.length ? 'blue' : undefined}
                style={{ cursor: 'pointer' }}
                onClick={() =>
                  setSelectedRegions(
                    selectedRegions.length === allRegions.length ? [] : [...allRegions]
                  )
                }
              >
                全选
              </Tag>
            </Space>
          </div>
          <Select
            mode="multiple"
            style={{ width: '100%' }}
            placeholder="选择城市"
            value={selectedRegions}
            onChange={setSelectedRegions}
            options={allRegions.map((r) => ({ label: r, value: r }))}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <Button
            type="primary"
            icon={<RocketOutlined />}
            size="large"
            loading={launching}
            disabled={!!runningTask && runningTask.status === 'running'}
            onClick={startScrape}
          >
            开始采集
          </Button>
          <span style={{ color: '#999' }}>
            <SearchOutlined /> 预计搜索 {selectedKeywords.length * selectedRegions.length} 次
          </span>
        </div>

        {runningTask && runningTask.status === 'running' && (
          <div style={{ marginTop: 16 }}>
            <Progress
              percent={
                runningTask.total_steps
                  ? Math.round((runningTask.progress / runningTask.total_steps) * 100)
                  : 0
              }
              status="active"
              format={() =>
                `${runningTask.progress}/${runningTask.total_steps} | 找到 ${runningTask.total_found} 条`
              }
            />
          </div>
        )}
      </Card>

      {stats && Object.keys(stats.by_status).length > 0 && (
        <Card title="状态分布" style={{ marginBottom: 24 }}>
          <Space wrap>
            {Object.entries(stats.by_status).map(([status, count]) => (
              <Tag key={status}>
                {status}: {count}
              </Tag>
            ))}
          </Space>
        </Card>
      )}
    </div>
  );
}
