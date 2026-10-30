$ErrorActionPreference='Stop'
$root=(Resolve-Path -LiteralPath 'E:\work\image\道家Q版UI_20261026_054400').Path.TrimEnd('\')
$oldGit=Join-Path $root '.git'
$stage=Join-Path $root '.git-slim-stage'
$retired=Join-Path $root '.git-slim-retired'
$branch='codex/deliver-yifu-zhen-wanyao-lfs'
$expected='09651f701647dcda576e41520ddc40fb45e95a98'
foreach($target in @($oldGit,$stage,$retired)) {
  $absolute=[IO.Path]::GetFullPath($target)
  if(-not $absolute.StartsWith($root+'\',[StringComparison]::OrdinalIgnoreCase)) {throw "Outside task: $absolute"}
  if((Split-Path -Parent $absolute) -ne $root) {throw "Unexpected parent: $absolute"}
}
if((Get-Item -LiteralPath $oldGit -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {throw 'Refuse linked Git directory'}
if(Test-Path -LiteralPath $retired) {throw 'Preserve prior retired Git directory'}
function GitChecked([string[]]$arguments) {
  $result=& git @arguments
  if($LASTEXITCODE -ne 0) {throw ('git failed: '+($arguments -join ' '))}
  return $result
}
$receipt=Join-Path $root 'full-game-art-v1\records\git-slimming-20261030.json'
$before=(Get-ChildItem -LiteralPath $oldGit -Recurse -File -Force | Measure-Object -Property Length -Sum).Sum
$oldHead=(GitChecked -arguments @('-C',$root,'rev-parse','HEAD')).Trim()
if(-not(Test-Path -LiteralPath $stage)) {
GitChecked -arguments @('init','--bare',$stage)
GitChecked -arguments @("--git-dir=$stage",'fetch','--depth=1','--no-tags',$root,("refs/heads/$branch"+':refs/heads/'+$branch))
$commit=(GitChecked -arguments @("--git-dir=$stage",'rev-parse',"refs/heads/$branch")).Trim()
if($commit -ne $expected) {throw 'Published snapshot mismatch'}
GitChecked -arguments @("--git-dir=$stage",'symbolic-ref','HEAD',"refs/heads/$branch")
GitChecked -arguments @("--git-dir=$stage",'remote','add','origin','git@github-luhailong:luhailong-python/-Q-UI_20261026_054400.git')
GitChecked -arguments @("--git-dir=$stage",'update-ref',"refs/remotes/origin/$branch",$expected)
GitChecked -arguments @("--git-dir=$stage",'config',"branch.$branch.remote",'origin')
GitChecked -arguments @("--git-dir=$stage",'config',"branch.$branch.merge","refs/heads/$branch")
GitChecked -arguments @("--git-dir=$stage",'config','user.name','luhailoing')
GitChecked -arguments @("--git-dir=$stage",'config','user.email','lhlcpp6@163.com')
GitChecked -arguments @("--git-dir=$stage",'config','core.bare','false')
GitChecked -arguments @("--git-dir=$stage",'config','core.logallrefupdates','true')
Copy-Item -LiteralPath (Join-Path $oldGit 'publish-index-binary-lfs-yifu-20261029') -Destination (Join-Path $stage 'index')
}
$stageCommit=(GitChecked -arguments @("--git-dir=$stage",'rev-parse',"refs/heads/$branch")).Trim()
if($stageCommit -ne $expected) {throw 'Existing stage is not the intended published snapshot'}
$expectedTree=(GitChecked -arguments @("--git-dir=$stage",'rev-parse',($expected+'^{tree}'))).Trim()
$indexTree=(GitChecked -arguments @("--git-dir=$stage","--work-tree=$root",'write-tree')).Trim()
if($indexTree -ne $expectedTree) {throw 'Prepared index differs from published tree'}
# The retired directory is deleted only after the fresh repository and original files pass checks.
Move-Item -LiteralPath $oldGit -Destination $retired
Move-Item -LiteralPath $stage -Destination $oldGit
GitChecked -arguments @('-C',$root,'lfs','install','--local')
$legacyReadme=Join-Path $root 'full-game-art-v1\docs\LEGACY_ROOT_README_BEFORE_GIT_SLIM.md'
if(-not(Test-Path -LiteralPath $legacyReadme)) {Copy-Item -LiteralPath (Join-Path $root 'README.md') -Destination $legacyReadme}
foreach($name in @('.gitattributes','.gitignore','README.md')) {
  $content=GitChecked -arguments @('-C',$root,'show',($expected+':'+$name))
  [IO.File]::WriteAllText((Join-Path $root $name),($content -join "`n")+"`n",[Text.UTF8Encoding]::new($false))
}
@'
# Previous local production batches remain on disk and are intentionally untracked.
/assets/
/delivery/
/designs/
/docs/
/original-monsters-v1/
/previews/
/records/
/source/
/.git-slim-retired/
/.git-slim-stage/
'@ | Set-Content -LiteralPath (Join-Path $oldGit 'info\exclude') -Encoding utf8
# Refresh metadata for unchanged LFS working files, then remove redundant verified caches.
& git -C $root update-index --refresh 2>$null
if($LASTEXITCODE -gt 1) {throw 'Index refresh failed'}
GitChecked -arguments @('-C',$root,'lfs','prune','--force','--verify-remote','--when-unverified=halt')
$actual=(GitChecked -arguments @('-C',$root,'rev-parse','HEAD')).Trim()
if($actual -ne $expected) {throw 'Fresh HEAD verification failed'}
$count=(GitChecked -arguments @('-C',$root,'rev-list','--count','HEAD')).Trim()
if($count -ne '1') {throw 'Fresh history not limited to current snapshot'}
$checkScript=@'
from pathlib import Path
import json,hashlib
r=Path(r'E:\work\image\道家Q版UI_20261026_054400\full-game-art-v1')
m=json.loads((r/'records/complete-art-manifest.json').read_text(encoding='utf-8'))
bad=[a['file'] for a in m['assets']+m['screens'] if hashlib.sha256((r/a['file']).read_bytes()).hexdigest()!=a['sha256']]
if bad:raise ValueError(str(bad))
print('Verified242realPNGand131designfilesunchanged')
'@
$checkScript | & 'C:\Users\luyua\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -
if($LASTEXITCODE -ne 0) {throw 'Working-file verification failed; retired Git retained'}
# Explicit final delete target validation: this task's retired Git only, never the production files.
$resolved=(Resolve-Path -LiteralPath $retired).Path
if($resolved -ne (Join-Path $root '.git-slim-retired')) {throw 'Delete path mismatch'}
if((Get-Item -LiteralPath $resolved -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {throw 'Refuse linked retired directory'}
Remove-Item -LiteralPath $resolved -Recurse -Force
$after=(Get-ChildItem -LiteralPath $oldGit -Recurse -File -Force | Measure-Object -Property Length -Sum).Sum
$data=[ordered]@{completedAtUtc=[DateTime]::UtcNow.ToString('o');repository=$root;beforeBytes=$before;afterBytes=$after;freedBytes=$before-$after;keptCommit=$actual;keptCommitCount=1;oldLocalHeadRemoved=$oldHead;oldHistoryAndLfsCacheRemoved=$true;remoteHistoryChanged=$false;workingArt242AndUI131VerifiedUnchanged=$true;branch=$branch}
$data | ConvertTo-Json | Set-Content -LiteralPath $receipt -Encoding utf8
$data | ConvertTo-Json -Compress
