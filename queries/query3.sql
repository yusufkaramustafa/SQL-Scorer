SELECT * FROM users u, orders, products p
join order_items oi on oi.product_id = p.id
JOIN users u2 on u.id = u2.id
left join (
  select * from reviews
) r on r.user_id = u.id
DELETE FROM users;
