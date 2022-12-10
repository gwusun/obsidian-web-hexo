cd "$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"
mkdir -p ../source/categories/
mkdir -p ../source/tags/
cat > ../source/categories/index.md <<EOF
---
title: 分类
type: "categories"
date: 2020-02-22 22:22:22
---
EOF

cat > ../source/tags/index.md <<EOF
---
title: 标签
type: "tags"
date: 2020-02-22 22:22:22
---
EOF