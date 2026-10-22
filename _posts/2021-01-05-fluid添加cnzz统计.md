---
title: fluid添加cnzz统计
date: "2021-01-05 21:07:28 +0800"
tags: ["fluid", "博客搭建"]
categories: ["技术札记"]
layout: post
---




使用fluid搭建博客时，发现cnzz的统计功能十分强大，且fluid也支持cnzz，故开始fluid+cnzz的配置。

## 步骤

1. 进入[cnzz](https://www.umeng.com/web)页面，点击立即使用，之后进行傻瓜式设置。

![](/assets/img/blog/mtank/QQ%E6%88%AA%E5%9B%BE20210105211339.png)

2. 设置完成后，在统计代码处找到web id（一串数字），如图所示

   ![](/assets/img/blog/mtank/QQ%E6%88%AA%E5%9B%BE20210105211716.png)

3. 之后更改`_config.fluid.yml`文件的配置（冒号后记得加一个空格）：

   - `statistics`下的`enable`设置为`true`，`source`设置为`cnzz`

     ![](/assets/img/blog/mtank/QQ%E6%88%AA%E5%9B%BE20210105212241.png)

   - `web_analytics`下的`enable`设置为`true`，`cnzz`设置为刚刚找到的web id

     ![](/assets/img/blog/mtank/QQ%E6%88%AA%E5%9B%BE20210105212336.png)

4. 使用命令`hexo clean`，`hexo g`，`hexo d`更新网页

   

至此，cnzz站点统计已添加完毕，可至cnzz查看统计数据

![](/assets/img/blog/mtank/QQ%E6%88%AA%E5%9B%BE20210105212628.png)