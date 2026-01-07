import math

class Type1:
    """
    模拟 JS 中的 a 类 (Scrambler Type 1) 的逻辑。
    Type 1 密钥是纯数字字符串。
    """
    def __init__(self, key_h: str, key_s: str):
        self.Tt = self._parse_key(key_s)  # Scramble Map
        self.Pt = self._parse_key(key_h)  # Unscramble Map
        
        # 验证解析是否成功且结构一致
        if not self.Tt or not self.Pt or \
           self.Tt['ndx'] != self.Pt['ndx'] or \
           self.Tt['ndy'] != self.Pt['ndy']:
            raise ValueError("Invalid Scrambler Type 1 keys or structure mismatch.")

    def _parse_key(self, key: str) -> dict | None:
        """ 模拟 a.prototype.Ct(t): 解析密钥字符串 """
        # 密钥格式示例: "2-2-eM"
        
        parts = key.split('-')
        if len(parts) != 3:
            return None

        # ndx, ndy 是网格尺寸
        ndx = int(parts[0])
        ndy = int(parts[1])
        data_str = parts[2]
        
        if len(data_str) != ndx * ndy * 2:
            return None

        def decode_char(t: str) -> tuple[int, int]:
            """ 模拟 a.prototype.At(t): 将 Base64-like 字符解码为 (i, i+2*n) """
            i = 0  # i: 0 或 1 (代表是否为大写)
            n = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".find(t)
            if n < 0:
                n = "abcdefghijklmnopqrstuvwxyz".find(t)
                i = 1
            else:
                i = 0
            
            # 返回: 0 或 1，以及 0 + 2*n 或 1 + 2*n
            return i, i + 2 * n

        pieces = []
        for d in range(ndx * ndy):
            # s, h 是 i, i+2*n 的解码结果
            i_s, s = decode_char(data_str[2 * d])
            i_h, h = decode_char(data_str[2 * d + 1])

            # 模拟 JS 中的逻辑来确定 w (宽度因子) 和 h (高度因子)
            # 这部分是 Type 1 的核心规则：根据在网格中的位置确定瓦片大小
            
            # (n-1)*(r-1) - 1: 瓦片总数 - (n+r-2) - 1
            a = (ndx - 1) * (ndy - 1) - 1
            # n-1 + a : 倒数第二行瓦片的起点
            f = ndx - 1 + a
            # r-1 + f : 最后一列瓦片的起点
            c = ndy - 1 + f
            l = 1 + c

            u, o = 0, 0 # w, h

            if d <= a:          # 瓦片在内部 (2x2)
                u = 2
                o = 2
            elif d <= f:        # 瓦片在右侧边界 (2x1)
                u = 2
                o = 1
            elif d <= c:        # 瓦片在底部边界 (1x2)
                u = 1
                o = 2
            elif d <= l:        # 瓦片在右下角 (1x1)
                u = 1
                o = 1
            
            # NOTE: 这里的 s, h 对应 JS 的 s, h，但其值是 0 到 61 的解码结果，在 JS 中是直接用于计算 x, y 的，
            # 而不是我们前面计算的 i + 2*n。原始 JS 代码在 decode_char 后的 s/h 变量名有歧义，
            # 但从上下文来看，这里应该直接使用 decode_char 的第二个返回值 (即 i + 2*n) 作为 s 和 h 的值。
            # s, h 实际上是瓦片在逻辑网格中的 x, y 坐标，值范围 [0, 2*ndx - 1] 和 [0, 2*ndy - 1]
            
            pieces.append({
                'x': s,  # 0 to 2*ndx - 1
                'y': h,  # 0 to 2*ndy - 1
                'w': u,  # 1 or 2
                'h': o   # 1 or 2
            })
            
        return {'ndx': ndx, 'ndy': ndy, 'piece': pieces}

    def calculate_coords(self, image_width: int, image_height: int) -> list:
        """ 模拟 a.prototype.Ot(t): 计算重组坐标 """
        t = {'width': image_width, 'height': image_height}
        
        # 1. 瓦片基准尺寸计算 (核心难点，涉及对齐)
        
        # 水平方向 (X)
        # n: 宽度对 8 取模
        n = t['width'] - t['width'] % 8 
        # r: 水平瓦片基准尺寸的倍数 (对 7 取模，再对 8 取模)
        r = math.floor((n - 1) / 7) - math.floor((n - 1) / 7) % 8 
        # e: 剩余宽度
        e = n - 7 * r 
        
        # 垂直方向 (Y)
        s = t['height'] - t['height'] % 8
        h = math.floor((s - 1) / 7) - math.floor((s - 1) / 7) % 8
        u = s - 7 * h

        # 2. 计算重组坐标
        coords = []
        o = len(self.Tt['piece']) # 瓦片总数
        
        for a in range(o):
            f = self.Tt['piece'][a] # 源瓦片信息 (Scramble Map)
            c = self.Pt['piece'][a] # 目标瓦片信息 (Unscramble Map)

            # 源坐标 (xsrc, ysrc, width, height)
            # xsrc: math.floor(f.x / 2) * r + f.x % 2 * e
            xsrc = math.floor(f['x'] / 2) * r + (f['x'] % 2) * e
            ysrc = math.floor(f['y'] / 2) * h + (f['y'] % 2) * u
            
            # width/height: math.floor(f.w / 2) * r + f.w % 2 * e
            # f['w'] (width factor) 是 1 或 2，f['w'] % 2 决定是否使用剩余尺寸 e/u
            width = math.floor(f['w'] / 2) * r + (f['w'] % 2) * e
            height = math.floor(f['h'] / 2) * h + (f['h'] % 2) * u
            
            # 目标坐标 (xdest, ydest)
            xdest = math.floor(c['x'] / 2) * r + (c['x'] % 2) * e
            ydest = math.floor(c['y'] / 2) * h + (c['y'] % 2) * u
            
            coords.append({
                'xsrc': xsrc, 'ysrc': ysrc, 'width': width, 'height': height,
                'xdest': xdest, 'ydest': ydest
            })

        # 3. 处理剩余边界 (右侧和底部)
        l = r * (self.Tt['ndx'] - 1) + e # 瓦片重排区域的最终宽度
        v = h * (self.Tt['ndy'] - 1) + u # 瓦片重排区域的最终高度
        
        # 右侧边界
        if l < t['width']:
            coords.append({
                'xsrc': l, 'ysrc': 0, 'width': t['width'] - l, 'height': v,
                'xdest': l, 'ydest': 0
            })
        # 底部边界
        if v < t['height']:
            coords.append({
                'xsrc': 0, 'ysrc': v, 'width': t['width'], 'height': t['height'] - v,
                'xdest': 0, 'ydest': v
            })
            
        return coords

class Type2:
    """
    模拟 JS 中的 f 类 (Scrambler Type 2) 的逻辑。
    Type 2 密钥是 Base64-like 编码的字符串。
    """
    # 模拟 JS 中的 f.Jt 字符映射表 (用于将 Base64-like 字符解码为数字)
    # 这是 Base64 的变种，需要精确匹配。
    _Jt = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 62, -1, -1, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, -1, -1, -1, -1, -1, -1, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, -1, -1, -1, -1, 63, -1, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, -1, -1, -1, -1, -1]
    
    def __init__(self, key_h: str, key_s: str):
        """输入时应当颠倒两个参数，即输入key_h为key_s，输入key_s为key_h，目前未确定原因"""
        self.kt = None # 最终的置换图
        self.T = 0     # 水平瓦片数量
        self.j = 0     # 垂直瓦片数量
        self.Dt = 0    # 边界宽度/高度
        self.Rt = []   # (Scramble) 垂直偏移调整因子
        self.Ft = []   # (Scramble) 水平偏移调整因子
        self.Lt = []   # (Unscramble) 垂直偏移调整因子
        self.Nt = []   # (Unscramble) 水平偏移调整因子
        
        self._parse_keys(key_s, key_h)
        
    def _decode_char(self, char_code: int) -> int:
        """ 模拟 f.Jt: Base64-like 字符到数字的映射 (0-63) """
        if 0 <= char_code < len(self._Jt):
            return self._Jt[char_code]
        return -1 # 返回 -1 对应无效字符

    def _parse_sub_key(self, data_str: str) -> dict[str, list[int]]:
        """ 模拟 f.prototype.Ct(t): 解析子密钥数据 """
        t_list, n_list, p_list = [], [], []
        
        # 1. T 个字符 -> t_list (水平偏移调整因子)
        for i in range(self.T):
            n = self._decode_char(ord(data_str[i]))
            t_list.append(n)
            
        # 2. j 个字符 -> n_list (垂直偏移调整因子)
        for i in range(self.j):
            n = self._decode_char(ord(data_str[self.T + i]))
            n_list.append(n)
            
        # 3. T*j 个字符 -> p_list (置换图/索引)
        for i in range(self.T * self.j):
            n = self._decode_char(ord(data_str[self.T + self.j + i]))
            p_list.append(n)
            
        return {'t': t_list, 'n': n_list, 'p': p_list}

    def _parse_keys(self, key_s: str, key_h: str):
        """ 解析 Scramble Map (key_s) 和 Unscramble Map (key_h) """
        # 密钥格式示例: =8-8+2-AbCd... (key_s) 和 =8-8-2-EfGh... (key_h)
        
        # 正则表达式匹配密钥结构
        import re
        s_match = re.match(r'^=([0-9]+)-([0-9]+)([-+])([0-9]+)-([-_0-9A-Za-z]+)$', key_s)
        h_match = re.match(r'^=([0-9]+)-([0-9]+)([-+])([0-9]+)-([-_0-9A-Za-z]+)$', key_h)

        if not s_match or not h_match: return
        
        # 结构校验
        if s_match.group(1) != h_match.group(1) or \
           s_match.group(2) != h_match.group(2) or \
           s_match.group(4) != h_match.group(4) or \
           s_match.group(3) != '+' or h_match.group(3) != '-':
            return

        self.T = int(s_match.group(1)) # 水平瓦片数量
        self.j = int(s_match.group(2)) # 垂直瓦片数量
        self.Dt = int(s_match.group(4))# 边界宽度
        
        # 瓦片数量校验
        if self.T > 8 or self.j > 8 or self.T * self.j > 64: return
        
        # 解析子密钥数据
        s_data_str = s_match.group(5)
        h_data_str = h_match.group(5)

        if len(s_data_str) != self.T + self.j + self.T * self.j or \
           len(h_data_str) != self.T + self.j + self.T * self.j:
            return

        s_parsed = self._parse_sub_key(s_data_str)
        h_parsed = self._parse_sub_key(h_data_str)

        self.Rt = s_parsed['n']  # Scramble: 垂直偏移调整因子 (j 个)
        self.Ft = s_parsed['t']  # Scramble: 水平偏移调整因子 (T 个)
        self.Lt = h_parsed['n']  # Unscramble: 垂直偏移调整因子 (j 个)
        self.Nt = h_parsed['t']  # Unscramble: 水平偏移调整因子 (T 个)
        
        # 构建最终的置换图 (this.kt)
        self.kt = []
        for u in range(self.T * self.j):
            # Scramble 置换图 (s_parsed['p']) 的第 u 个值
            # 作为 Unscramble 置换图 (h_parsed['p']) 的索引
            # 最终的值才是实际的置换索引
            final_index = s_parsed['p'][h_parsed['p'][u]]
            self.kt.append(final_index)
            
    def calculate_coords(self, image_width: int, image_height: int) -> list:
        """ 模拟 f.prototype.Ot(t): 计算重组坐标 """
        if not self.kt:
            # 如果密钥解析失败，则返回 1:1 映射 (无加密)
            return [{
                'xsrc': 0, 'ysrc': 0, 'width': image_width, 'height': image_height,
                'xdest': 0, 'ydest': 0
            }]

        t = {'width': image_width, 'height': image_height}
        
        # 1. 计算核心重排区域的尺寸
        i = t['width'] - 2 * self.T * self.Dt  # 瓦片总宽度
        n = t['height'] - 2 * self.j * self.Dt # 瓦片总高度
        
        # 2. 计算瓦片基准尺寸 (r, s) 和剩余尺寸 (e, h)
        # r: 水平基准宽度， e: 水平剩余宽度
        r = math.floor((i + self.T - 1) / self.T) # 水平瓦片的平均尺寸
        e = i - (self.T - 1) * r                   # 最后一个水平瓦片的尺寸 (或剩余尺寸)
        
        s = math.floor((n + self.j - 1) / self.j) # 垂直瓦片的平均尺寸
        h = n - (self.j - 1) * s                   # 最后一个垂直瓦片的尺寸 (或剩余尺寸)
        
        # 3. 遍历置换图计算坐标
        u = [] # 存储坐标
        for o in range(self.T * self.j):
            # (o % self.T) 是瓦片在网格中的水平索引 (0 到 T-1)
            # math.floor(o / self.T) 是瓦片在网格中的垂直索引 (0 到 j-1)
            a = o % self.T    # 水平网格索引
            f = math.floor(o / self.T) # 垂直网格索引
            
            # --- 确定源坐标 (xsrc, ysrc) ---
            
            # c: 水平起始位置 (含边界 Dt)
            # Scramble: Lt 是垂直偏移调整因子, Nt 是水平偏移调整因子
            c = self.Dt + a * (r + 2 * self.Dt) + (e - r if self.Lt[f] < a else 0) 
            # l: 垂直起始位置 (含边界 Dt)
            l = self.Dt + f * (s + 2 * self.Dt) + (h - s if self.Nt[a] < f else 0) 
            
            # --- 确定目标坐标 (xdest, ydest) ---
            
            # v: 目标瓦片的水平索引 (从置换图 kt 中获取)
            v = self.kt[o] % self.T
            # d: 目标瓦片的垂直索引
            d = math.floor(self.kt[o] / self.T)
            
            # b: 目标水平起始位置 (不含边界 Dt)
            # Unscramble: Rt 是垂直偏移调整因子, Ft 是水平偏移调整因子
            b = v * r + (e - r if self.Rt[d] < v else 0) 
            # g: 目标垂直起始位置 (不含边界 Dt)
            g = d * s + (h - s if self.Ft[v] < d else 0)
            
            # --- 确定瓦片尺寸 (p, m) ---
            
            # p: 瓦片宽度 (使用剩余尺寸 e 还是基准尺寸 r)
            p = e if self.Lt[f] == a else r 
            # m: 瓦片高度 (使用剩余尺寸 h 还是基准尺寸 s)
            m = h if self.Nt[a] == f else s 

            if i > 0 and n > 0:
                u.append({
                    'xsrc': c, 'ysrc': l, 'width': p, 'height': m,
                    'xdest': b, 'ydest': g
                })
                
        # 4. (Type 2 没有额外的边界处理，因为它将边界本身作为瓦片的一部分来处理了)

        return u