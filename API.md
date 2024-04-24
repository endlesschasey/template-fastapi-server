# 创建音乐

## 默认模式请求参数（对象）(generate)

```sh
songTitle 歌曲名称
songDescription 歌曲描述
instrumentalState 纯音乐状态
```

## 自定义模式请求参数（对象）(custom_generate)

```sh
songTitle 歌曲名称
songLyrics 歌词
songStyles 音乐风格
instrumentalState 纯音乐状态
```

## 响应参数（对象）：生成完后再给我响应，前端一直等待（最长等待 4 分钟）

```sh
songId 歌曲ID
songTitle 歌曲名称
songStyles 音乐风格
songImg 音乐专辑图
songUrl 音乐资源链接
downloadUrl 下载链接
```

# 获取音乐列表(song_list)

## 请求参数（对象）

```sh
pageSize:Number 每页显示数量（数字）
pageNum:Number 当前页码（数字）
```

## 响应参数（对象）

```sh
songsList:[] 歌曲列表（数组）
total:Number 总数（数字）
```

# 删除音乐(delete_song)

## 请求参数

```sh
songId 歌曲ID（数字）
```

## 响应参数

```sh
code:Number 状态码（数字）
message:String 提示信息（字符串）
```

# 音乐详情(song_info)

## 请求参数（对象）

```sh
songId 歌曲ID（数字）
```

## 响应参数（对象）

```sh
songId 歌曲ID（数字）
songImg 音乐专辑图
songTitle 歌曲名称（字符串）
songStyles 音乐风格
songCreateTime 创建时间（字符串）2024年4月24日
songDescription 歌曲描述
songLyrics 歌词
```

# 获取当日额度(GET)(get_credits)

## 响应参数

```
credits : int
```