"""Offline delivery estimates; all fixture edits use a temporary database."""

import pytest

from agent import db, tools
from agent.agent import TOOLS_BY_ROLE
from agent.auth import AuthContext


@pytest.mark.parametrize("ctx", [
    AuthContext(user_id=1, role="shopper"),
    AuthContext(user_id=9002, role="merchant", store_id=2),
    AuthContext(user_id=9501, role="support"),
])
def test_delivery_estimate_aggregates_without_private_orders(world_copy, ctx):
    with db.connection() as conn:
        conn.execute("UPDATE orders SET status = 'placed' WHERE product_id = 1")
        ids = [r[0] for r in conn.execute("SELECT id FROM orders ORDER BY id LIMIT 5")]
        for order_id, status, delivery in zip(
            ids,
            ['delivered', 'refunded', 'delivered', 'shipped', 'delivered'],
            ['2026-01-05', '2026-01-09', '2025-12-31', '2026-01-30', None],
        ):
            conn.execute(
                "UPDATE orders SET product_id=1, ordered_at='2026-01-01', status=?, delivered_at=? WHERE id=?",
                (status, delivery, order_id),
            )
        conn.commit()
    result = tools.estimate_delivery_time(ctx, 1)
    assert result['average_days'] == 6.0
    assert result['sample_count'] == 2
    assert set(result) == {'ok', 'product_id', 'average_days', 'sample_count', 'basis', 'note'}
    assert 'estimate_delivery_time' in [tool.name for tool in TOOLS_BY_ROLE[ctx.role]]


def test_delivery_estimate_missing_history_and_product(world_copy):
    ctx = AuthContext(user_id=1, role='shopper')
    with db.connection() as conn:
        conn.execute("UPDATE orders SET delivered_at=NULL WHERE product_id=1")
        conn.commit()
    result = tools.estimate_delivery_time(ctx, 1)
    assert result['ok'] is True
    assert result['average_days'] is None
    assert result['sample_count'] == 0
    assert tools.estimate_delivery_time(ctx, 999999)['error'] == 'not_found'
