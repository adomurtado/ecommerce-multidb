-- Cek node yang terdaftar
SELECT * FROM master_get_active_worker_nodes();

-- Cek table yang di-shard atau direplikasi
SELECT logicalrelid::text AS table_name,
       partmethod,
       partkey
FROM pg_dist_partition;

-- Cek detail shard yang dibuat
SELECT * FROM pg_dist_shard LIMIT 10;

-- Cek peletakan shard di node (placement)
SELECT shardid, nodename, nodeport
FROM pg_dist_placement
JOIN pg_dist_node ON pg_dist_placement.groupid = pg_dist_node.groupid
LIMIT 10;

-- Cek apakah produk dan users adalah reference table
SELECT logicalrelid::text, partmethod
FROM pg_dist_partition
WHERE logicalrelid::text IN ('produk', 'users');
