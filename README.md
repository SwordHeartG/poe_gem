# poe_gem

### 使用方式
* 安装python环境与依赖包
* 先执行gem_price.py
* 再执行gem_analysis_lvl1.py 和 gem_analysis_lvl20.py
* 两个gem_analysis中需要csv的导入路径，日期需要修改为获取gem_price的日期。
----
* 做lvl1和lvl20两个表，是因为个别宝石满级不是20级，另外有些宝石20级价格会高更多，推荐放一起参考着看。
* 最后一列置信度：集市数量小于5个，置信度低；小于10个中等；大于10个高
* 透镜价格是按ninja价格的1.25倍计算的，因为批量买透镜会有溢价，按批量价格算成本会更准确些
