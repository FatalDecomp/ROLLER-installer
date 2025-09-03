"""GitHub client for fetching ROLLER release information."""

from typing import Optional, List, Dict, Any
from github import Github
from github.GithubException import GithubException
import logging

logger = logging.getLogger(__name__)


class RollerGitHubClient:
    """Client for interacting with ROLLER GitHub releases."""

    def __init__(self):
        """Initialize GitHub client for fataldecomp/roller repository."""
        self.github = Github()
        self.repo_name = "FatalDecomp/ROLLER"
        try:
            self.repo = self.github.get_repo(self.repo_name)
        except GithubException as e:
            logger.error(f"Failed to connect to repository {self.repo_name}: {e}")
            raise

    def get_latest_prerelease_tag(self) -> Optional[str]:
        """Get the tag name of the latest pre-release.
        
        Returns:
            Tag name of the latest pre-release, or None if not found
        """
        try:
            releases = self.repo.get_releases()
            prereleases = []
            
            # Collect all pre-releases
            for release in releases:
                if release.prerelease:
                    prereleases.append(release)
            
            if not prereleases:
                logger.warning("No pre-releases found")
                return None
            
            # Sort by published date (newest first)
            prereleases.sort(key=lambda r: r.published_at, reverse=True)
            latest = prereleases[0]
            
            logger.info(f"Found latest pre-release: {latest.tag_name} (published: {latest.published_at})")
            return latest.tag_name
            
        except GithubException as e:
            logger.error(f"Failed to fetch releases: {e}")
            raise

    def get_latest_release_tag(self, include_prerelease: bool = True) -> Optional[str]:
        """Get the tag name of the latest release.
        
        Args:
            include_prerelease: Whether to include pre-releases
            
        Returns:
            Tag name of the latest release, or None if not found
        """
        try:
            if include_prerelease:
                # Get the absolute latest release (pre-release or stable)
                releases = self.repo.get_releases()
                for release in releases:
                    logger.info(f"Found latest release: {release.tag_name} (prerelease: {release.prerelease})")
                    return release.tag_name
            else:
                # Get latest stable release only
                try:
                    latest = self.repo.get_latest_release()
                    logger.info(f"Found latest stable release: {latest.tag_name}")
                    return latest.tag_name
                except GithubException:
                    logger.warning("No stable releases found")
                    return None
                    
            logger.warning("No releases found")
            return None
        except GithubException as e:
            logger.error(f"Failed to fetch latest release: {e}")
            raise

    def get_release_by_tag(self, tag: str) -> Optional[Dict[str, Any]]:
        """Get release information by tag name.
        
        Args:
            tag: Release tag name
            
        Returns:
            Dictionary with release information, or None if not found
        """
        try:
            release = self.repo.get_release(tag)
            return {
                'tag_name': release.tag_name,
                'name': release.title,
                'prerelease': release.prerelease,
                'published_at': release.published_at,
                'body': release.body,
                'assets': [{
                    'name': asset.name,
                    'size': asset.size,
                    'download_url': asset.browser_download_url
                } for asset in release.assets]
            }
        except GithubException as e:
            logger.error(f"Failed to fetch release {tag}: {e}")
            return None

    def list_releases(self, limit: int = 10, include_prerelease: bool = True) -> List[Dict[str, Any]]:
        """List recent releases.
        
        Args:
            limit: Maximum number of releases to return
            include_prerelease: Whether to include pre-releases
            
        Returns:
            List of release information dictionaries
        """
        try:
            releases = []
            for release in self.repo.get_releases():
                if not include_prerelease and release.prerelease:
                    continue
                    
                releases.append({
                    'tag_name': release.tag_name,
                    'name': release.title,
                    'prerelease': release.prerelease,
                    'published_at': release.published_at,
                    'body': release.body[:200] + '...' if len(release.body) > 200 else release.body
                })
                
                if len(releases) >= limit:
                    break
                    
            logger.info(f"Found {len(releases)} releases")
            return releases
        except GithubException as e:
            logger.error(f"Failed to list releases: {e}")
            raise

    def check_for_updates(self, current_version: str, include_prerelease: bool = True) -> Optional[Dict[str, Any]]:
        """Check if a newer version is available.
        
        Args:
            current_version: Current installed version tag
            include_prerelease: Whether to check pre-releases
            
        Returns:
            Dictionary with newer release info, or None if up to date
        """
        latest_tag = self.get_latest_release_tag(include_prerelease)
        
        if latest_tag and latest_tag != current_version:
            logger.info(f"Update available: {current_version} -> {latest_tag}")
            return self.get_release_by_tag(latest_tag)
        
        logger.info(f"Already up to date: {current_version}")
        return None
