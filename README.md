# myIPTVs

#### 介绍

收集IPTV信息，数据来源于 https://github.com/iptv-org/api

#### 软件架构

基于python和MongoDB，将数据刷新到内存数据库。
EPG信息从网络爬取，按照频道采集后，写入带TTL索引的表，过期自动删除。


