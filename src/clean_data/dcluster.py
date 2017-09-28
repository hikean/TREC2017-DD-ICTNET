#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import math
from operator import itemgetter


def get_simddC(d, dj, clstRank, bestDockRank, rankcd):
    def get_wqc(K, clstRank, bestDockRank):
        return {
            c: ((K - clstRank[c] + 1) +
                (1.0 / bestDockRank.get(c, 1000))) * 0.5
            for c in clstRank
        }

    def r(c, d):
        return rankcd[c].get(d, 1e10) ** (-0.5)

    K = len(clstRank)
    w = get_wqc(K, clstRank, bestDockRank)

    def _simddC(d, dj, Cluster):
        return 2.0 * (
            1 - 1.0 / (
                1 + math.exp(
                    -sum([
                        w[c] * math.fabs(r(c, d) - r(c, dj))
                        for c in Cluster
                    ])
                )
            )
        )
    return _simddC(d, dj, clstRank)


def get_dSn(d, Sn, clstRank, bestDockRank, rankcd):
    return 1 - max(
        get_simddC(d, dj, clstRank, bestDockRank, rankcd)
        for dj in Sn
    )


def next_doc(RestDocs, Sn, rqd, p, clstRank, bestDockRank, rankcd):
    def r(d):
        return rqd[d]

    def compute(d):
        return (
            p * r(d) + (1.0 - p) *
            get_dSn(d, Sn, clstRank, bestDockRank, rankcd)
        )

    item = max(
        [(d, compute(d)) for d in (set(RestDocs) - set(Sn))],
        key=itemgetter(1)
    )
    return item[0]
