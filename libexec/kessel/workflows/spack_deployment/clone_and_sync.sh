src_checkout="$1"
src=$(git -C "$1" rev-parse --absolute-git-dir)
src_rev=$(git -C "$1" rev-parse HEAD)
dest="$2"
echo "$src -> $dest"
$KESSEL_ROOT/libexec/kessel/tools/update_local_branches "$src_checkout"
git -c advice.detachedhead=false -C "$src_checkout" checkout "$src_rev"
git -C "$src_checkout" fetch --tags
mkdir -p $(dirname "$dest")
rm -rf "$dest"
git -c advice.detachedhead=false clone "$src" "$dest"
git -C "$dest" fetch --tags
$KESSEL_ROOT/libexec/kessel/tools/update_local_branches "$dest"
git -c advice.detachedhead=false -C "$dest" checkout "$src_rev"
