#!/usr/bin/env python3
import argparse

import cereal.messaging as messaging


def can_table(dat):
  header = [str(n) for n in range(7, -1, -1)] + [' ']
  rows = []
  for b in dat:
    bits = list(bin(b)[2:].zfill(8))
    row = bits + [hex(b)]
    rows.append(row)
  col_widths = [max(len(header[i]), max(len(row[i]) for row in rows)) for i in range(len(header))]
  header_line = " | ".join(header[i].rjust(col_widths[i]) for i in range(len(header)))
  sep_line = "-+-".join('-' * col_widths[i] for i in range(len(header)))
  row_lines = []
  for row in rows:
    row_lines.append(" | ".join(row[i].rjust(col_widths[i]) for i in range(len(row))))
  table = f"{header_line}\n{sep_line}\n" + "\n".join(row_lines)
  return table


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Cabana-like table of bits for your terminal",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("addr", type=str, nargs=1)
  parser.add_argument("bus", type=int, default=0, nargs='?')

  args = parser.parse_args()

  addr = int(args.addr[0], 0)
  can = messaging.sub_sock('can', conflate=False, timeout=None)

  print(f"waiting for {hex(addr)} ({addr}) on bus {args.bus}...")

  latest = None
  while True:
    for msg in messaging.drain_sock(can, wait_for_one=True):
      for m in msg.can:
        if m.address == addr and m.src == args.bus:
          latest = m

    if latest is None:
      continue

    table = can_table(latest.dat)
    print(f"\n\n{hex(addr)} ({addr}) on bus {args.bus}\n{table}")
