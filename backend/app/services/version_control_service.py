"""Version Control Service - 分支和提交管理"""
from typing import Optional, List
from datetime import datetime
from sqlmodel import Session, func
from app.models.branch import PromptBranch
from app.models.commit import PromptCommit
from app.models.prompt import Prompt
from app.models.user import User


class VersionControlService:
    """版本控制核心服务"""

    def create_branch(self, db: Session, prompt_id: int, name: str,
                      base_branch_id: Optional[int] = None,
                      user_id: int = None, description: str = None) -> PromptBranch:
        """
        创建新分支

        Args:
            db: 数据库会话
            prompt_id: Prompt ID
            name: 分支名
            base_branch_id: 基准分支（基于哪个分支创建）
            user_id: 创建者 ID
            description: 分支描述

        Returns:
            PromptBranch
        """
        # 检查分支名唯一性
        existing = db.query(PromptBranch).filter(
            PromptBranch.prompt_id == prompt_id,
            PromptBranch.name == name
        ).first()
        if existing:
            raise ValueError(f"分支 {name} 已存在")

        branch = PromptBranch(
            prompt_id=prompt_id,
            name=name,
            description=description,
            base_branch_id=base_branch_id,
            is_default=False,
            created_by=user_id
        )
        db.add(branch)
        db.commit()
        db.refresh(branch)

        # 如果有基准分支，基于该分支最后一个 commit 创建初始提交
        if base_branch_id:
            last_commit = db.query(PromptCommit).filter(
                PromptCommit.branch_id == base_branch_id
            ).order_by(PromptCommit.created_at.desc()).first()

            if last_commit:
                initial_commit = PromptCommit(
                    branch_id=branch.id,
                    parent_id=last_commit.id,
                    title=f"基于分支创建",
                    content=last_commit.content,
                    variables_schema=last_commit.variables_schema,
                    created_by=user_id
                )
                db.add(initial_commit)
                db.commit()

        return branch

    def get_branches(self, db: Session, prompt_id: int) -> List[PromptBranch]:
        """获取 prompt 的所有分支"""
        return db.query(PromptBranch).filter(
            PromptBranch.prompt_id == prompt_id
        ).order_by(PromptBranch.created_at.desc()).all()

    def get_branch(self, db: Session, branch_id: int) -> Optional[PromptBranch]:
        """获取分支"""
        return db.query(PromptBranch).get(branch_id)

    def delete_branch(self, db: Session, branch_id: int) -> bool:
        """删除分支（不能删除默认分支）"""
        branch = db.query(PromptBranch).get(branch_id)
        if not branch:
            raise ValueError("分支不存在")
        if branch.is_default:
            raise ValueError("不能删除默认分支")

        # 检查是否有未合并的 PR
        from app.models.pull_request import PromptPullRequest
        open_prs = db.query(PromptPullRequest).filter(
            PromptPullRequest.source_branch_id == branch_id,
            PromptPullRequest.status == 'open'
        ).count()
        if open_prs > 0:
            raise ValueError("该分支有未关闭的 PR，不能删除")

        db.delete(branch)
        db.commit()
        return True

    def create_commit(self, db: Session, branch_id: int, user_id: int,
                     title: str, content: str,
                     variables_schema: dict = None) -> PromptCommit:
        """
        创建新提交

        Args:
            db: 数据库会话
            branch_id: 分支 ID
            user_id: 创建者 ID
            title: 提交信息
            content: prompt 内容
            variables_schema: 变量定义

        Returns:
            PromptCommit
        """
        # 获取当前分支的最新提交
        last_commit = db.query(PromptCommit).filter(
            PromptCommit.branch_id == branch_id
        ).order_by(PromptCommit.created_at.desc()).first()

        commit = PromptCommit(
            branch_id=branch_id,
            parent_id=last_commit.id if last_commit else None,
            title=title,
            content=content,
            variables_schema=variables_schema,
            created_by=user_id
        )
        db.add(commit)
        db.commit()
        db.refresh(commit)

        return commit

    def get_commits(self, db: Session, branch_id: int,
                    page: int = 1, page_size: int = 20) -> dict:
        """
        分页获取提交历史

        Returns:
            {"items": [...], "total": int, "page": int, "page_size": int}
        """
        total = db.query(func.count(PromptCommit.id)).filter(
            PromptCommit.branch_id == branch_id
        ).scalar()

        commits = db.query(PromptCommit).filter(
            PromptCommit.branch_id == branch_id
        ).order_by(
            PromptCommit.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()

        return {
            'items': commits,
            'total': total,
            'page': page,
            'page_size': page_size
        }

    def get_commit(self, db: Session, commit_id: int) -> Optional[PromptCommit]:
        """获取特定提交"""
        return db.query(PromptCommit).get(commit_id)

    def get_branch_content(self, db: Session, branch_id: int) -> Optional[str]:
        """获取分支当前最新内容"""
        last_commit = db.query(PromptCommit).filter(
            PromptCommit.branch_id == branch_id
        ).order_by(PromptCommit.created_at.desc()).first()

        return last_commit.content if last_commit else None

    def revert_to_commit(self, db: Session, branch_id: int,
                         target_commit_id: int, user_id: int) -> PromptCommit:
        """
        回滚到指定版本（创建新提交）

        Args:
            db: 数据库会话
            branch_id: 分支 ID
            target_commit_id: 目标提交 ID
            user_id: 操作者 ID

        Returns:
            新创建的提交
        """
        target_commit = db.query(PromptCommit).get(target_commit_id)
        if not target_commit:
            raise ValueError("提交不存在")

        # 创建新提交，内容为目标版本
        return self.create_commit(
            db=db,
            branch_id=branch_id,
            user_id=user_id,
            title=f"Revert to: {target_commit.title}",
            content=target_commit.content,
            variables_schema=target_commit.variables_schema
        )

    def initialize_default_branch(self, db: Session, prompt_id: int, user_id: int) -> PromptBranch:
        """
        为 prompt 初始化默认分支（main）

        当 prompt 创建时自动调用
        """
        # 检查是否已有默认分支
        existing = db.query(PromptBranch).filter(
            PromptBranch.prompt_id == prompt_id,
            PromptBranch.is_default == True
        ).first()
        if existing:
            return existing

        branch = self.create_branch(
            db=db,
            prompt_id=prompt_id,
            name="main",
            user_id=user_id,
            description="默认分支"
        )
        branch.is_default = True
        db.commit()
        db.refresh(branch)

        # 更新 prompt 的 default_branch_id
        prompt = db.query(Prompt).get(prompt_id)
        if prompt:
            prompt.default_branch_id = branch.id
            db.commit()

        return branch


# 全局实例
version_control_service = VersionControlService()