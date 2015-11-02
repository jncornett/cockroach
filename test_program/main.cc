#include <initializer_list>
#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>

template<typename T>
struct Buffer
{
    std::vector<T> data;
    typename std::vector<T>::size_type pos = 0;

    T& peek()
    { return data[pos]; }

    T& read()
    { return data[pos++]; }

    void seek(typename std::vector<T>::size_type off)
    { pos = off; }

    bool eof() const
    { return pos >= data.size(); }

    Buffer(typename std::vector<T>::size_type n) :
        data(n) { }

    template<typename U>
    Buffer(std::initializer_list<U> il) :
        data(il) { }

    template<typename U>
    Buffer(const std::vector<U>& v) :
        data(v) { }
};

template<typename T, typename std::vector<T>::size_type N>
struct VM
{
    using Op = void(*)(VM&);

    VM(std::initializer_list<std::pair<char, Op>> il) :
        instr(il), mem(N) { }

    VM(std::vector<std::pair<char, Op>> v) :
        instr(v), mem(N) { }

    void reset()
    {
        mem.clear();
        instr.seek(0);
    }

    void run()
    {
        while ( !instr.eof() )
        { instr.read().second(*this); }
    }

    void debug()
    {
        while ( !instr.eof() )
        {
            show_state(instr.peek().first);
            instr.read().second(*this);
        }
    }

    void show_state(char i)
    {
        std::cerr << "[" << instr.pos << "] " << i << std::endl;
        show_mem();
    }

    void show_mem()
    {
        std::cerr << "  ";

        size_t i = 0;
        for ( auto c : mem.data )
        {
            std::cerr << static_cast<int>(c);
            if ( i++ == mem.pos )
                std::cerr << "* ";
            else
                std::cerr << "  ";
        }

        std::cerr << std::endl;
    }

    Buffer<std::pair<char, Op>> instr;
    Buffer<T> mem;
};

namespace Ops
{
    constexpr size_t mem_size = 16;
    using data_type = char;
    using VM = ::VM<data_type, mem_size>;

    void ret(VM&);

    void jump(VM& vm)
    {
        if ( vm.mem.peek() )
            return;

        while ( !vm.instr.eof() && vm.instr.read().second != ret );
    }

    void ret(VM& vm)
    {
        while ( vm.instr.pos && vm.instr.peek().second != jump )
            vm.instr.pos--;
    }

    void inc_val(VM& vm)
    { vm.mem.data[vm.mem.pos]++; }

    void dec_val(VM& vm)
    { vm.mem.data[vm.mem.pos]--; }

    void inc_ptr(VM& vm)
    { vm.mem.pos++; }

    void dec_ptr(VM& vm)
    { vm.mem.pos--; }

    void output(VM& vm)
    { std::cout << vm.mem.peek(); }
}

static std::unordered_map<char, Ops::VM::Op> op_map {
    { '[', Ops::jump },
    { ']', Ops::ret },
    { '>', Ops::inc_ptr },
    { '<', Ops::dec_ptr },
    { '+', Ops::inc_val },
    { '-', Ops::dec_val },
    { '.', Ops::output }
};

std::vector<std::pair<char, Ops::VM::Op>> interpret(std::string script)
{
    std::vector<std::pair<char, Ops::VM::Op>> ops;

    for ( char c : script )
    {
        auto search = op_map.find(c);
        if ( search != op_map.end() )
            ops.push_back(std::make_pair(search->first, search->second));
    }

    return ops;
}

int main()
{
    auto compiled = interpret(
        "+++++++++[->++++++++<]>.<"
        "+++++++[->++++<]>+."
        "+++++++.."
        "+++.>"
        "++++++++[->++++<]>.<"
        "++++++++++[->+++++<]>+++++.<"
        "++++++[->++++<]>."
        "+++."
        "------."
        "--------.>"
        "++++++++++[->+++<]>+++.<"
        "+++++++[->---<]>-."
    );
    Ops::VM vm(compiled);
    vm.run();

    return 0;
}
