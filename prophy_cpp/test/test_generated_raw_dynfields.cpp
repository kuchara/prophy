#include <gtest/gtest.h>
#include "util.hpp"
#include "Dynfields.pp.hpp"

using namespace testing;

TEST(generated_raw_dynfields, Dynfields)
{
    test_swap<Dynfields>(
        "\x00\x00\x00\x05"
        "\x01\x02\x03\x04"
        "\x05\xFF\xFF\xFF"

        "\x00\x00\x00\x03"
        "\x00\x01\x00\x02"
        "\x00\x03\xFF\xFF"

        "\x00\x00\x00\x00\x00\x00\x00\x01",

        "\x05\x00\x00\x00"
        "\x01\x02\x03\x04"
        "\x05\xFF\xFF\xFF"
        "\x03\x00\x00\x00"
        "\x01\x00\x02\x00"
        "\x03\x00\xFF\xFF"
        "\x01\x00\x00\x00\x00\x00\x00\x00"
    );
}

TEST(generated_raw_dynfields, DynfieldsOverlapped)
{
    test_swap<DynfieldsOverlapped>(
        "\x00\x00\x00\x01"
        "\x00\x00\x00\x03"
        "\x00\x0B\x00\xBB\x0B\xBB"
        "\x00\x04"
        "\x00\x0C\x00\xCC"
        "\x0C\xCC\xCC\xCC"
        "\x00\x01\xFF\xFF",

        "\x01\x00\x00\x00"
        "\x03\x00\x00\x00"
        "\x0B\x00\xBB\x00\xBB\x0B"
        "\x04\x00"
        "\x0C\x00\xCC\x00"
        "\xCC\x0C\xCC\xCC"
        "\x01\x00\xFF\xFF"
    );
}

TEST(generated_raw_dynfields, DynfieldsPadded)
{
    test_swap<DynfieldsPadded>(
        "\x01\xFF\xFF\xFF\xFF\xFF\xFF\xFF"
        "\x00\x00\x00\x03"
        "\x01\x02\x03\xFF"
        "\x00\x00\x00\x02"
        "\x04\x05\xFF\xFF"
        "\x00\x00\x00\x00\x00\x00\x00\x06",

        "\x01\xFF\xFF\xFF\xFF\xFF\xFF\xFF"
        "\x03\x00\x00\x00"
        "\x01\x02\x03\xFF"
        "\x02\x00\x00\x00"
        "\x04\x05\xFF\xFF"
        "\x06\x00\x00\x00\x00\x00\x00\x00"
    );
}

TEST(generated_raw_dynfields, DynfieldsFixtail)
{
    test_swap<DynfieldsFixtail>(
        "\x00\x00\x00\x03"
        "\x01\x02\x03\xFF"
        "\xAA\xBB\xCC\xDD" "\xFF\xFF\xFF\xFF"
        "\xAA\xBB\xCC\xDD\xEE\xFF\x01\x02",

        "\x03\x00\x00\x00"
        "\x01\x02\x03\xFF"
        "\xDD\xCC\xBB\xAA" "\xFF\xFF\xFF\xFF"
        "\x02\x01\xFF\xEE\xDD\xCC\xBB\xAA"
    );
}

TEST(generated_raw_dynfields, DynfieldsComp)
{
    test_swap<DynfieldsComp>(
        "\x00\x00\x00\x01"
        "\xAA\xBB\xCC\xDD"
        "\x00\x00\x00\x03"
        "\xAA\xBB\xCC\xDD"
        "\xAA\xBB\xCC\xDD"
        "\xAA\xBB\xCC\xDD"
        "\x00\x00\x00\x02"
        "\xAA\xBB\xCC\xDD"
        "\xAA\xBB\xCC\xDD",

        "\x01\x00\x00\x00"
        "\xDD\xCC\xBB\xAA"
        "\x03\x00\x00\x00"
        "\xDD\xCC\xBB\xAA"
        "\xDD\xCC\xBB\xAA"
        "\xDD\xCC\xBB\xAA"
        "\x02\x00\x00\x00"
        "\xDD\xCC\xBB\xAA"
        "\xDD\xCC\xBB\xAA"
    );
}
