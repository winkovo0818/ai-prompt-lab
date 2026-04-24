"""Pull Request Service"""
from typing import Optional, List
from datetime import datetime
from sqlmodel import Session, func
from app.models.pull_request import PromptPullRequest
from app.models.branch import PromptBranch
from app.models.commit import PromptCommit


class PullRequestService:
    """Pull Request 服务"""

    def create_pr(self, db: Session, prompt_id: int,
                  source_branch_id: int, target_branch_id: int,
                  title: str, author_id: int,
                  description: str = None) -> PromptPullRequest:
        """创建 PR"""
        # 检查分支是否存在
        source = db.query(PromptBranch).get(source_branch_id)
        target = db.query(PromptBranch).get(target_branch_id)

        if not source or not target:
            raise ValueError("分支不存在")

        if source.prompt_id != prompt_id or target.prompt_id != prompt_id:
            raise ValueError("分支不属于该 Prompt")

        if source_branch_id == target_branch_id:
            raise ValueError("源分支和目标分支不能相同")

        pr = PromptPullRequest(
            prompt_id=prompt_id,
            source_branch_id=source_branch_id,
            target_branch_id=target_branch_id,
            title=title,
            description=description,
            author_id=author_id,
            status='open'
        )
        db.add(pr)
        db.commit()
        db.refresh(pr)

        return pr

    def get_pr(self, db: Session, pr_id: int) -> Optional[PromptPullRequest]:
        """获取 PR"""
        return db.query(PromptPullRequest).get(pr_id)

    def get_prs(self, db: Session, prompt_id: int,
                status: str = None, page: int = 1, page_size: int = 10) -> dict:
        """
        获取 PR 列表

        Args:
            prompt_id: Prompt ID
            status: 过滤状态（open/merged/closed）
            page: 页码
            page_size: 每页数量
        """
        query = db.query(PromptPullRequest).filter(
            PromptPullRequest.prompt_id == prompt_id
        )

        if status:
            query = query.filter(PromptPullRequest.status == status)

        total = query.count()

        prs = query.order_by(
            PromptPullRequest.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()

        return {
            'items': prs,
            'total': total,
            'page': page,
            'page_size': page_size
        }

    def can_merge(self, db: Session, pr_id: int) -> dict:
        """检查 PR 是否可以合并"""
        pr = db.query(PromptPullRequest).get(pr_id)
        if not pr or pr.status != 'open':
            return {'can_merge': False, 'reason': 'PR 已关闭或不存在'}

        # 获取源分支和目标分支的最新提交
        source_commit = db.query(PromptCommit).filter(
            PromptCommit.branch_id == pr.source_branch_id
        ).order_by(PromptCommit.created_at.desc()).first()

        target_commit = db.query(PromptCommit).filter(
            PromptCommit.branch_id == pr.target_branch_id
        ).order_by(PromptCommit.created_at.desc()).first()

        return {
            'can_merge': True,
            'source_commit_id': source_commit.id if source_commit else None,
            'target_commit_id': target_commit.id if target_commit else None
        }

    def merge(self, db: Session, pr_id: int, user_id: int,
              merge_method: str = 'squash') -> dict:
        """合并 PR"""
        pr = db.query(PromptPullRequest).get(pr_id)
        if not pr:
            raise ValueError("PR 不存在")

        can_merge = self.can_merge(db, pr_id)
        if not can_merge['can_merge']:
            raise ValueError(can_merge['reason'])

        new_commit_id = None

        if merge_method == 'squash':
            # 压缩合并：将源分支的所有提交压缩成一个
            source_commits = db.query(PromptCommit).filter(
                PromptCommit.branch_id == pr.source_branch_id
            ).order_by(PromptCommit.created_at.asc()).all()

            # 找到目标分支的最新提交
            target_last = db.query(PromptCommit).filter(
                PromptCommit.branch_id == pr.target_branch_id
            ).order_by(PromptCommit.created_at.desc()).first()

            # 获取源分支最后一个提交的内容
            last_source = source_commits[-1] if source_commits else None

            if last_source:
                # 在目标分支创建新提交
                from app.services.version_control_service import version_control_service
                new_commit = version_control_service.create_commit(
                    db=db,
                    branch_id=pr.target_branch_id,
                    user_id=user_id,
                    title=f"Merge '{pr.title}'",
                    content=last_source.content,
                    variables_schema=last_source.variables_schema
                )
                new_commit_id = new_commit.id

        # 更新 PR 状态
        pr.status = 'merged'
        pr.merged_by = user_id
        pr.merged_at = datetime.utcnow()
        db.commit()

        return {
            'merged': True,
            'new_commit_id': new_commit_id
        }

    def close_pr(self, db: Session, pr_id: int, user_id: int) -> PromptPullRequest:
        """关闭 PR"""
        pr = db.query(PromptPullRequest).get(pr_id)
        if not pr:
            raise ValueError("PR 不存在")

        if pr.status != 'open':
            raise ValueError("只能关闭 open 状态的 PR")

        pr.status = 'closed'
        db.commit()
        db.refresh(pr)

        return pr

    def update_pr_reviewers(self, db: Session, pr_id: int,
                            reviewer_id: int = None) -> PromptPullRequest:
        """更新 PR 审核人"""
        pr = db.query(PromptPullRequest).get(pr_id)
        if not pr:
            raise ValueError("PR 不存在")

        pr.reviewer_id = reviewer_id
        db.commit()
        db.refresh(pr)

        return pr


# 全局实例
pull_request_service = PullRequestService()