"""导出服务 - 封装现有导出逻辑"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from server.models import Lead
from exporter import export_to_excel


def export_leads(leads: list[Lead]) -> str:
    """将 Lead 模型列表导出为 Excel，返回文件路径"""
    companies = []
    for lead in leads:
        companies.append({
            "name": lead.name,
            "phone": lead.phone or "",
            "city": lead.city or "",
            "district": lead.district or "",
            "address": lead.address or "",
            "region": lead.region or "",
            "industry": lead.industry or "",
            "source": lead.source or "",
            "search_keyword": lead.search_keyword or "",
        })
    return export_to_excel(companies)
