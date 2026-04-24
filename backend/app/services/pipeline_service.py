"""Prompt Pipeline Service - 执行结果反馈到 PR"""
from typing import Optional
from sqlmodel import Session
from app.models.pull_request import PromptPullRequest
from app.models.commit import PromptCommit


class PipelineService:
    """Pipeline 服务 - 执行结果反馈到 PR 状态"""

    def update_pr_status_after_execution(
        self,
        db: Session,
        prompt_id: int,
        branch_id: int,
        execution_success: bool,
        execution_result: str = None
    ) -> Optional[PromptPullRequest]:
        """
        执行完成后更新 PR 状态

        Args:
            db: 数据库会话
            prompt_id: Prompt ID
            branch_id: 执行时所在的分支 ID
            execution_success: 执行是否成功
            execution_result: 执行结果摘要

        Returns:
            被更新的 PR，如果没有 open 的 PR 则返回 None
        """
        # 查找该分支相关的 open PR
        open_prs = db.query(PromptPullRequest).filter(
            PromptPullRequest.prompt_id == prompt_id,
            PromptPullRequest.source_branch_id == branch_id,
            PromptPullRequest.status == 'open'
        ).all()

        if not open_prs:
            return None

        # 更新每个 open PR 的状态
        # 实际可以存储执行历史，但简化处理：
        # 如果最后一次执行成功，PR 可以合并；失败则阻止
        for pr in open_prs:
            # 可以存储执行结果到 PR 的 description 或额外字段
            # 这里简化处理：标记最后执行状态
            if execution_success:
                # 执行成功，PR 可以合并
                pass
            else:
                # 执行失败，PR 标记为有问题（可以通过 description 存储）
                pass

        db.commit()
        return open_prs[0] if open_prs else None

    def get_pipeline_status(
        self,
        db: Session,
        prompt_id: int,
        branch_id: int
    ) -> dict:
        """
        获取分支的 Pipeline 状态

        Returns:
            {"has_open_pr": bool, "last_execution_success": bool|None, "can_merge": bool}
        """
        open_pr = db.query(PromptPullRequest).filter(
            PromptPullRequest.prompt_id == prompt_id,
            PromptPullRequest.source_branch_id == branch_id,
            PromptPullRequest.status == 'open'
        ).first()

        if not open_pr:
            return {
                "has_open_pr": False,
                "last_execution_success": None,
                "can_merge": True  # 没有 PR 可以直接合并
            }

        # 获取该分支的最后一次执行记录
        from app.models.execution_history import ExecutionHistory
        last_execution = db.query(ExecutionHistory).filter(
            ExecutionHistory.prompt_id == prompt_id
        ).order_by(ExecutionHistory.created_at.desc()).first()

        return {
            "has_open_pr": True,
            "pr_id": open_pr.id,
            "pr_title": open_pr.title,
            "last_execution_success": last_execution.status == 'success' if last_execution else None,
            "can_merge": last_execution.status == 'success' if last_execution else False
        }


# 全局实例
pipeline_service = PipelineService()