# 现代 C++ 规则

命名、排版、注释与类型遵循本技能其余规则，仓库配置和实际语言版本优先。C 工程不套用 C++ 类型和语法。

## 资源与类型

- 用 RAII 表达所有权，优先标准容器、流、智能指针或带清理器的句柄；裸指针可用于非拥有观察和必要的 C API 适配，不把所有裸指针都当作泄漏。
- 智能指针按独占/共享所有权选型，不默认 shared_ptr。确需手工分配的底层适配应封装释放路径，普通业务代码避免裸 new/delete。
- noexcept 要覆盖成员构造、分配与调用链；不能因为函数体没有 throw 就标记。析构函数不向外传播异常，移动操作仅在实际保证不抛时标记 noexcept。
- auto、范围 for、constexpr、nullptr 按可读性和语言版本采用；concept 需要 C++20。不要用移动/完美转发取代正常的值语义，返回局部值时避免无理由的 std::move 破坏拷贝消除。
- 标准容器和字符串优先；需要 C 数组布局或零结尾接口时保留适配边界。string_view 不拥有数据，也不保证结尾为零；传给 C 字符串 API 前处理长度和生命周期。
- 使用具名转换并核对范围、符号和对象生命周期；不能把 static_cast 当成运行时检查。
- 锁使用 RAII。性能决定依据测量和调用场景，不凭“热路径”一词禁止所有虚调用。

## 组织与依赖

- 头文件应可独立包含。前向声明仅用于不需要完整定义且不会破坏公共接口的情况；需要完整类型时正确 include。
- 模板、内联、constexpr 等定义按可见性要求放置，不机械要求所有实现进入 .cpp。
- 类和函数按职责拆分，不用固定方法数/行数迫使无意义拆分。包含顺序和格式服从仓库配置，未指定时沿用本技能排版规则。

## 完整示例

以下示例采用业务模块驼峰命名；显式复制路径，拒绝内嵌零字符，使用流管理资源，并保留文件中的零字节。调用方可用异常区分打开失败与读取失败。

```cpp
/**
 * @file  file_processor.hpp
 * @brief 通过 RAII 流读取文件内容
 */
#pragma once

#include <array>
#include <fstream>
#include <stdexcept>
#include <string>
#include <string_view>

class FileProcessor
{
public:
    /**
     * @brief 打开指定文件
     * @param[in] path 文件路径视图，不得包含零字符
     * @throws std::invalid_argument 路径包含零字符
     * @throws std::runtime_error 无法打开文件
     */
    explicit FileProcessor(std::string_view path)
    {
        if (path.find('\0') != std::string_view::npos)
        {
            throw std::invalid_argument("Path contains a NUL character");
        }
        m_file.open(std::string(path), std::ios::binary);
        if (!m_file)
        {
            throw std::runtime_error("Cannot open file: " + std::string(path));
        }
    }

    /**
     * @brief 从当前位置读取剩余字节
     * @return 文件剩余内容，允许包含零字节
     * @throws std::runtime_error 读取失败
     */
    std::string readAll()
    {
        std::string            content;
        std::array<char, 4096> buffer{};

        while (m_file)
        {
            m_file.read(buffer.data(), static_cast<std::streamsize>(buffer.size()));
            content.append(buffer.data(), static_cast<std::size_t>(m_file.gcount()));
        }
        if (!m_file.eof())
        {
            throw std::runtime_error("Cannot read file");
        }
        return content;
    }

private:
    std::ifstream m_file;
};
```

该示例的路径语义由标准库和平台决定；Windows 上需要完整 Unicode 路径支持时，应使用项目已有的 filesystem/path 方案。它不承诺所有窄字符串编码均可作为系统路径。
