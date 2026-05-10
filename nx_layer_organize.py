# =============================================================================
# NX 2406 Layer Organization Tool
# =============================================================================
# 适用版本: Siemens NX 2406
# 功能说明: 将当前 Work Part 中非实体、非组件对象移动到 255 图层
# 安全限制: 
#   - 不删除任何对象
#   - 不隐藏任何对象  
#   - 不修改实体对象图层
#   - 不修改装配组件图层
#   - 不自动保存文件
#   - 仅处理当前 Work Part，不递归处理子零件
# 作者: Sisyphus
# 日期: 2026-05-11
# =============================================================================

import NXOpen
import NXOpen.UF
import NXOpen.Features
import NXOpen.Assemblies
from typing import List, Tuple, Dict, Any

# =============================================================================
# 配置常量
# =============================================================================
TARGET_LAYER = 255          # 目标图层
TOOL_VERSION = "1.0.0"      # 工具版本


# =============================================================================
# 获取 NX Session
# 来源: E:\NX2406\UGOPEN\pythonStubs\NXOpen\__init__.pyi
#       class Session: @staticmethod def GetSession() -> Session
# =============================================================================
def get_session() -> NXOpen.Session:
    """获取当前 NX Session"""
    return NXOpen.Session.GetSession()


# =============================================================================
# 获取 Work Part
# 来源: E:\NX2406\UGOPEN\pythonStubs\NXOpen\__init__.pyi
#       class PartCollection: @property def Work(self) -> Part
# =============================================================================
def get_work_part(session: NXOpen.Session) -> NXOpen.Part:
    """获取当前 Work Part"""
    return session.Parts.Work


# =============================================================================
# 打开 Listing Window
# 来源: E:\NX2406\UGOPEN\pythonStubs\NXOpen\__init__.pyi
#       class Session: ListingWindow 属性
#       class ListingWindow: def Open(self), def WriteLine(self, text)
# =============================================================================
def open_listing_window(session: NXOpen.Session) -> NXOpen.ListingWindow:
    """打开并返回 Listing Window"""
    listing_window = session.ListingWindow
    listing_window.Open()
    return listing_window


# =============================================================================
# 获取对象类型名称
# 来源: E:\NX2406\UGOPEN\pythonStubs\NXOpen\__init__.pyi
#       class NXObject: @property def Name(self) -> str
#                     : def GetType() -> Type (继承自 System.Object)
# =============================================================================
def get_object_type_name(obj: NXOpen.NXObject) -> str:
    """获取对象的类型名称"""
    if obj is None:
        return "None"
    try:
        return obj.GetType().Name
    except:
        return "Unknown"


# =============================================================================
# 判断是否为 Component 对象
# 来源: E:\NX2406\UGOPEN\pythonStubs\NXOpen\Assemblies\__init__.pyi
#       class Component: 继承自 NXOpen.DisplayableObject
# 方法: isinstance(obj, NXOpen.Assemblies.Component)
# =============================================================================
def is_component_object(obj: NXOpen.NXObject) -> bool:
    """判断对象是否为装配组件"""
    try:
        return isinstance(obj, NXOpen.Assemblies.Component)
    except Exception as e:
        # 如果类型检查失败，尝试通过对象类型名称判断
        try:
            return "Component" in obj.GetType().Name
        except:
            return False


# =============================================================================
# 判断是否为 Body 对象
# 来源: E:\NX2406\UGOPEN\pythonStubs\NXOpen\__init__.pyi
#       class Body: 继承自 DisplayableObject
# =============================================================================
def is_body_object(obj: NXOpen.NXObject) -> bool:
    """判断对象是否为 Body"""
    try:
        return isinstance(obj, NXOpen.Body)
    except:
        return False


# =============================================================================
# 判断是否为 Solid Body
# 来源: E:\NX2406\UGOPEN\pythonStubs\NXOpen\__init__.pyi
#       class Body: @property def IsSolidBody(self) -> bool
# =============================================================================
def is_solid_body(obj: NXOpen.Body) -> bool:
    """判断 Body 是否为实体"""
    try:
        return obj.IsSolidBody
    except:
        return False


# =============================================================================
# 判断是否为 Sheet Body
# 来源: E:\NX2406\UGOPEN\pythonStubs\NXOpen\__init__.pyi
#       class Body: @property def IsSheetBody(self) -> bool
# =============================================================================
def is_sheet_body(obj: NXOpen.Body) -> bool:
    """判断 Body 是否为片体"""
    try:
        return obj.IsSheetBody
    except:
        return False


# =============================================================================
# 判断对象是否可以安全移动
# 基于以下规则:
# 1. 不能是 Component (装配组件)
# 2. 如果是 Body，不能是 Solid Body (实体)
#       Sheet Body 可以移动，但需要确认能可靠区分
# 3. 其他对象类型视为可移动
# =============================================================================
def is_safe_to_move(obj: NXOpen.NXObject) -> Tuple[bool, str]:
    """
    判断对象是否可以安全移动
    返回: (是否可移动, 原因)
    """
    try:
        # 检查是否是 Component
        if is_component_object(obj):
            return False, "Assembly Component - should not be moved"
        
        # 检查是否是 Solid Body
        if is_body_object(obj):
            if is_solid_body(obj):
                return False, "Solid Body - should not be moved"
            # 对于 Sheet Body，我们允许移动，但需要谨慎
            # 因为 IsSheetBody 的可靠性已在 API 中确认
            return True, "Sheet Body - can be moved"
        
        # 其他对象类型视为可移动
        return True, "Non-body object - can be moved"
        
    except Exception as e:
        return False, f"Error checking safety: {str(e)}"


# =============================================================================
# 获取对象当前图层
# 来源: E:\NX2406\UGOPEN\pythonStubs\NXOpen\__init__.pyi
#       class DisplayableObject: @property def Layer(self) -> int
# =============================================================================
def get_object_layer(obj: NXOpen.DisplayableObject) -> int:
    """获取对象当前所在图层"""
    try:
        return obj.Layer
    except:
        return -1


# =============================================================================
# 移动对象到指定图层
# 来源: E:\NX2406\UGOPEN\pythonStubs\NXOpen\__init__.pyi
#       class DisplayableObject: @Layer.setter def Layer(self, layer: int)
# =============================================================================
def move_object_to_layer(obj: NXOpen.DisplayableObject, target_layer: int) -> Tuple[bool, str]:
    """
    将对象移动到指定图层
    返回: (是否成功, 错误信息)
    """
    try:
        obj.Layer = target_layer
        return True, ""
    except Exception as e:
        return False, str(e)


# =============================================================================
# 收集候选对象
# 从 Work Part 中收集所有可显示的对象
# =============================================================================
def collect_candidate_objects(work_part: NXOpen.Part) -> List[NXOpen.DisplayableObject]:
    """收集 Work Part 中的所有候选对象"""
    candidates = []
    
    try:
        # 遍历 Bodies
        # 来源: E:\NX2406\UGOPEN\pythonStubs\NXOpen\__init__.pyi
        #       class Part: Bodies 属性 (BodyCollection)
        if hasattr(work_part, 'Bodies') and work_part.Bodies is not None:
            for body in work_part.Bodies:
                if body is not None:
                    candidates.append(body)
    except Exception as e:
        # 记录错误但不中断
        pass
    
    try:
        # 遍历 Curves
        if hasattr(work_part, 'Curves') and work_part.Curves is not None:
            for curve in work_part.Curves:
                if curve is not None:
                    candidates.append(curve)
    except Exception as e:
        pass
    
    try:
        # 遍历 Points
        if hasattr(work_part, 'Points') and work_part.Points is not None:
            for point in work_part.Points:
                if point is not None:
                    candidates.append(point)
    except Exception as e:
        pass
    
    try:
        # 遍历 Features (可能包含 Sketch 等)
        if hasattr(work_part, 'Features') and work_part.Features is not None:
            for feature in work_part.Features:
                if feature is not None:
                    # SketchFeature 继承自 Feature
                    if isinstance(feature, NXOpen.Features.SketchFeature):
                        candidates.append(feature)
    except Exception as e:
        pass
    
    try:
        # 尝试获取 Datum 对象
        # 注意: Datum 对象可能在不同位置
        if hasattr(work_part, 'Datums'):
            for datum in work_part.Datums:
                if datum is not None:
                    candidates.append(datum)
    except Exception as e:
        pass
    
    # 获取组件
    try:
        if hasattr(work_part, 'ComponentAssembly') and work_part.ComponentAssembly is not None:
            comp_assembly = work_part.ComponentAssembly
            if hasattr(comp_assembly, 'RootComponent') and comp_assembly.RootComponent is not None:
                root = comp_assembly.RootComponent
                # 递归收集所有子组件
                candidates = collect_components_recursive(root, candidates)
    except Exception as e:
        pass
    
    return candidates


def collect_components_recursive(component, candidates: List) -> List:
    """递归收集组件及其子组件"""
    if component is None:
        return candidates
    
    try:
        candidates.append(component)
        # 获取子组件
        if hasattr(component, 'GetChildren'):
            children = component.GetChildren()
            for child in children:
                candidates = collect_components_recursive(child, candidates)
    except Exception as e:
        pass
    
    return candidates


# =============================================================================
# 生成报告
# =============================================================================
def generate_report(
    listing_window: NXOpen.ListingWindow,
    work_part: NXOpen.Part,
    stats: Dict[str, Any],
    moved_details: List[Dict],
    skipped_details: List[Dict],
    failed_details: List[Dict]
):
    """生成整理报告"""
    
    separator = "=" * 70
    
    listing_window.WriteLine(separator)
    listing_window.WriteLine("NX 图层整理工具 - 执行报告")
    listing_window.WriteLine(separator)
    listing_window.WriteLine("")
    
    # 基本信息
    listing_window.WriteLine("【基本信息】")
    listing_window.WriteLine(f"  工具版本: {TOOL_VERSION}")
    listing_window.WriteLine(f"  适用版本: NX 2406")
    listing_window.WriteLine(f"  目标图层: {TARGET_LAYER}")
    listing_window.WriteLine("")
    
    # 部件信息
    listing_window.WriteLine("【部件信息】")
    try:
        part_name = work_part.Name if hasattr(work_part, 'Name') else "Unknown"
        listing_window.WriteLine(f"  部件名称: {part_name}")
    except:
        listing_window.WriteLine(f"  部件名称: Unable to retrieve")
    
    try:
        # 尝试获取完整路径
        full_path = work_part.FullPath if hasattr(work_part, 'FullPath') else "N/A"
        listing_window.WriteLine(f"  完整路径: {full_path}")
    except:
        listing_window.WriteLine(f"  完整路径: Unable to retrieve")
    listing_window.WriteLine("")
    
    # 统计信息
    listing_window.WriteLine("【统计信息】")
    listing_window.WriteLine(f"  扫描对象总数: {stats.get('total', 0)}")
    listing_window.WriteLine(f"  成功移动数量: {stats.get('moved', 0)}")
    listing_window.WriteLine(f"  跳过对象数量: {stats.get('skipped', 0)}")
    listing_window.WriteLine(f"  失败对象数量: {stats.get('failed', 0)}")
    listing_window.WriteLine("")
    
    # 检测信息
    listing_window.WriteLine("【对象检测】")
    listing_window.WriteLine(f"  检测到装配组件: {'是' if stats.get('has_components', False) else '否'}")
    listing_window.WriteLine(f"  检测到实体对象: {'是' if stats.get('has_solids', False) else '否'}")
    listing_window.WriteLine(f"  检测到片体对象: {'是' if stats.get('has_sheets', False) else '否'}")
    listing_window.WriteLine("")
    
    # 按类型统计移动
    if moved_details:
        listing_window.WriteLine("【按类型统计 - 已移动】")
        type_counts = {}
        for detail in moved_details:
            obj_type = detail.get('type', 'Unknown')
            type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
        for obj_type, count in sorted(type_counts.items()):
            listing_window.WriteLine(f"  {obj_type}: {count}")
        listing_window.WriteLine("")
    
    # 按类型统计跳过
    if skipped_details:
        listing_window.WriteLine("【按类型统计 - 已跳过】")
        type_counts = {}
        for detail in skipped_details:
            obj_type = detail.get('type', 'Unknown')
            type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
        for obj_type, count in sorted(type_counts.items()):
            listing_window.WriteLine(f"  {obj_type}: {count}")
        listing_window.WriteLine("")
    
    # 失败详情
    if failed_details:
        listing_window.WriteLine("【失败对象详情】")
        for detail in failed_details:
            listing_window.WriteLine(f"  名称: {detail.get('name', 'N/A')}")
            listing_window.WriteLine(f"  类型: {detail.get('type', 'Unknown')}")
            listing_window.WriteLine(f"  原图层: {detail.get('original_layer', 'N/A')}")
            listing_window.WriteLine(f"  失败原因: {detail.get('error', 'Unknown')}")
            listing_window.WriteLine("  -" * 30)
        listing_window.WriteLine("")
    
    # 重要提示
    listing_window.WriteLine(separator)
    listing_window.WriteLine("【重要提示】")
    listing_window.WriteLine("  ⚠ 本脚本未自动保存文件，请手动检查后再保存！")
    listing_window.WriteLine("  ⚠ 如需撤销本次操作，请使用 NX 的撤销功能（Ctrl+Z）！")
    listing_window.WriteLine("  ⚠ 建议在正式使用前先在测试文件上验证！")
    listing_window.WriteLine(separator)


# =============================================================================
# 主函数
# =============================================================================
def main():
    """主函数"""
    
    # 获取 Session
    session = get_session()
    
    # 获取 Listing Window
    listing_window = open_listing_window(session)
    
    # 写入开始信息
    listing_window.WriteLine("")
    listing_window.WriteLine("NX Layer Organization Tool")
    listing_window.WriteLine(f"Version: {TOOL_VERSION}")
    listing_window.WriteLine("=" * 50)
    listing_window.WriteLine("")
    
    # 检查是否有 Work Part
    work_part = get_work_part(session)
    if work_part is None:
        listing_window.WriteLine("❌ 错误: 当前没有打开的 Work Part！")
        listing_window.WriteLine("   请先打开或新建一个部件文件。")
        return
    
    # 设置 Undo Mark
    # 来源: E:\NX2406\UGOPEN\pythonStubs\NXOpen\__init__.pyi
    #       class Session: def SetUndoMark(visibility, name) -> int
    undo_mark_id = None
    try:
        undo_mark_id = session.SetUndoMark(
            NXOpen.Session.MarkVisibility.Visible, 
            "Layer Organization"
        )
        listing_window.WriteLine(f"✓ 已设置 Undo Mark (ID: {undo_mark_id})")
        listing_window.WriteLine("")
    except Exception as e:
        listing_window.WriteLine(f"⚠ 警告: 无法设置 Undo Mark: {str(e)}")
        listing_window.WriteLine("")
    
    # 初始化统计
    stats = {
        'total': 0,
        'moved': 0,
        'skipped': 0,
        'failed': 0,
        'has_components': False,
        'has_solids': False,
        'has_sheets': False
    }
    
    moved_details = []
    skipped_details = []
    failed_details = []
    
    # 收集候选对象
    listing_window.WriteLine("正在扫描对象...")
    candidates = collect_candidate_objects(work_part)
    stats['total'] = len(candidates)
    listing_window.WriteLine(f"  找到 {len(candidates)} 个对象")
    listing_window.WriteLine("")
    
    # 处理每个对象
    listing_window.WriteLine("开始处理对象...")
    
    for obj in candidates:
        try:
            if obj is None:
                continue
            
            obj_name = getattr(obj, 'Name', 'Unnamed')
            obj_type = get_object_type_name(obj)
            original_layer = get_object_layer(obj)
            
            # 更新检测标志
            if is_component_object(obj):
                stats['has_components'] = True
            elif is_body_object(obj):
                if is_solid_body(obj):
                    stats['has_solids'] = True
                elif is_sheet_body(obj):
                    stats['has_sheets'] = True
            
            # 判断是否可以移动
            can_move, reason = is_safe_to_move(obj)
            
            if not can_move:
                # 跳过此对象
                stats['skipped'] += 1
                skipped_details.append({
                    'name': obj_name,
                    'type': obj_type,
                    'reason': reason
                })
                continue
            
            # 已经在目标图层的不处理
            if original_layer == TARGET_LAYER:
                stats['skipped'] += 1
                skipped_details.append({
                    'name': obj_name,
                    'type': obj_type,
                    'reason': f"Already on layer {TARGET_LAYER}"
                })
                continue
            
            # 尝试移动对象
            success, error = move_object_to_layer(obj, TARGET_LAYER)
            
            if success:
                stats['moved'] += 1
                moved_details.append({
                    'name': obj_name,
                    'type': obj_type,
                    'original_layer': original_layer
                })
            else:
                stats['failed'] += 1
                failed_details.append({
                    'name': obj_name,
                    'type': obj_type,
                    'original_layer': original_layer,
                    'error': error
                })
                
        except Exception as e:
            # 单个对象失败不应中断整个流程
            stats['failed'] += 1
            try:
                obj_name = getattr(obj, 'Name', 'Unnamed')
                obj_type = get_object_type_name(obj)
            except:
                obj_name = 'Unknown'
                obj_type = 'Unknown'
            
            failed_details.append({
                'name': obj_name,
                'type': obj_type,
                'original_layer': -1,
                'error': str(e)
            })
    
    listing_window.WriteLine(f"  处理完成: {stats['moved']} 移动, {stats['skipped']} 跳过, {stats['failed']} 失败")
    listing_window.WriteLine("")
    
    # 刷新显示，让图层变更在建模视图中生效
    # 来源: E:\NX2406\UGOPEN\pythonStubs\NXOpen\__init__.pyi
    #       class Update: static def DoUpdate(undo_mark: int) -> int
    if undo_mark_id is not None:
        try:
            NXOpen.Update.DoUpdate(undo_mark_id)
            listing_window.WriteLine("✓ 显示已刷新")
        except Exception as e:
            listing_window.WriteLine(f"⚠ 刷新显示失败: {str(e)}")
    
    # 生成详细报告
    generate_report(listing_window, work_part, stats, moved_details, skipped_details, failed_details)
    
    # 完成提示
    listing_window.WriteLine("")
    listing_window.WriteLine("✓ 图层整理完成！")
    listing_window.WriteLine("")


# =============================================================================
# 入口点
# =============================================================================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # 如果 Listing Window 已打开，写入错误
        try:
            session = get_session()
            listing_window = session.ListingWindow
            if listing_window is not None:
                listing_window.WriteLine(f"\n❌ 严重错误: {str(e)}\n")
        except:
            pass
        # 重新抛出异常以便调试
        raise
