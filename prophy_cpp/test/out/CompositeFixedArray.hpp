#ifndef _PROPHY_GENERATED_ScalarFixedArray_HPP
#define _PROPHY_GENERATED_ScalarFixedArray_HPP

#include <prophy/prophy.hpp>

#include "Scalar.hpp"

struct CompositeFixedArray
{
    Scalar a[3];
};

namespace prophy
{

inline CompositeFixedArray* swap(CompositeFixedArray& payload)
{
    swap_n_fixed(payload.a, 3);
    return &payload + 1;
}

} // namespace prophy

#endif  /* _PROPHY_GENERATED_ScalarFixedArray_HPP */
