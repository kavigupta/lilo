(* (\* let emd (ctx : Ctx.t) s s' = *\) *)
(* (\*   let emd, _ = *\) *)
(* (\*     Iter.int_range ~start:0 ~stop:(ctx.dim - 1) *\) *)
(* (\*     |> Iter.fold *\) *)
(* (\*          (fun (emd_tot, emd_prev) i -> *\) *)
(* (\*            let p = Bool.to_int (Set.mem s i) in *\) *)
(* (\*            let q = Bool.to_int (Set.mem s' i) in *\) *)
(* (\*            let emd = p + emd_prev - q in *\) *)
(* (\*            (emd_tot + abs emd, emd)) *\) *)
(* (\*          (0, 0) *\) *)
(* (\*   in *\) *)
(* (\*   emd *\) *)

(* let emd _ s s' = *)
(*   let _, _, emd = *)
(*     Set.merge_to_sequence ~order:`Increasing s s' *)
(*     |> Sequence.fold ~init:(0, 0, 0) ~f:(fun (emd_prev, prev_bucket, emd_tot) -> function *)
(*          | Set.Merge_to_sequence_element.Left bucket -> *)
(*              let emd = 1 + emd_prev in *)
(*              let emd_tot = emd_tot + abs ((bucket - prev_bucket) * emd_prev) + abs emd in *)
(*              (emd, bucket, emd_tot) *)
(*          | Right bucket -> *)
(*              let emd = emd_prev - 1 in *)
(*              let emd_tot = emd_tot + abs ((bucket - prev_bucket) * emd_prev) + abs emd in *)
(*              (emd, bucket, emd_tot) *)
(*          | Both (bucket, _) -> *)
(*              let emd = emd_prev in *)
(*              let emd_tot = emd_tot + abs ((bucket - prev_bucket) * emd_prev) + abs emd in *)
(*              (emd, bucket, emd_tot)) *)
(*   in *)
(*   emd *)

(* let blocks_distance ?(add_remove_penalty = 5) _ctx s s' = *)
(*   Map.fold_symmetric_diff s s' ~data_equal:[%equal: Set.M(Int).t * Set.M(Int).t] ~init:0 *)
(*     ~f:(fun d (_, rows) -> *)
(*       let l1_h, l1_v, emd_h, emd_v = *)
(*         match rows with *)
(*         | `Left (h_row, v_row) | `Right (h_row, v_row) -> *)
(*             (Set.length h_row, Set.length v_row, 0, 0) *)
(*         | `Unequal ((h_row, v_row), (h_row', v_row')) -> *)
(*             let l1_h = abs (Set.length h_row - Set.length h_row') in *)
(*             let l1_v = abs (Set.length v_row - Set.length v_row') in *)
(*             let emd_h = emd _ctx h_row h_row' in *)
(*             let emd_v = emd _ctx v_row v_row' in *)
(*             (l1_h, l1_v, emd_h, emd_v) *)
(*       in *)
(*       d + ((l1_h + l1_v) * add_remove_penalty) + emd_h + emd_v) *)

(* let row_distance s s' = *)
(*   let add_penalty = 1 and remove_penalty = 5 in *)
(*   if Set.is_empty s then Set.length s' * remove_penalty *)
(*   else if Set.is_empty s' then Set.length s * add_penalty *)
(*   else *)
(*     (\* let min = Set.min_elt_exn s in *\) *)
(*     (\* let min' = Set.min_elt_exn s' in *\) *)
(*     (\* let diff = min' - min in *\) *)
(*     (\* let s' = Set.map (module Int) ~f:(fun x -> x - diff) s' in *\) *)
(*     (\* diff *\) *)
(*     (\* + *\) *)
(*     (add_penalty * Set.length (Set.diff s s')) *)
(*     + (remove_penalty * Set.length (Set.diff s' s)) *)

(* let blocks_distance _ctx s s' = *)
(*   let n = Float.of_int @@ Set.length (Set.inter s s') in *)
(*   let d = Float.of_int @@ Set.length (Set.union s s') in *)
(*   if Float.(d = 0.) then 0. else 1. -. (n /. d) *)

(* let shift_down = *)
(*   Set.filter_map *)
(*     (module Block) *)
(*     ~f:(fun (b : Block.t) -> if b.y > 0 then Some { b with y = b.y - 1 } else None) *)

(* let shift_right (ctx : Ctx.t) bs = *)
(*   if (not (Set.is_empty bs)) && Set.for_all bs ~f:(fun (b : Block.t) -> b.x < ctx.dim - 1) *)
(*   then Some (Set.map (module Block) bs ~f:(fun (b : Block.t) -> { b with x = b.x + 1 })) *)
(*   else None *)

(* let shift_up (ctx : Ctx.t) bs = *)
(*   if (not (Set.is_empty bs)) && Set.for_all bs ~f:(fun (b : Block.t) -> b.y < ctx.dim - 1) *)
(*   then Some (Set.map (module Block) bs ~f:(fun (b : Block.t) -> { b with y = b.y + 1 })) *)
(*   else None *)

(* let shift_left bs = *)
(*   if (not (Set.is_empty bs)) && Set.for_all bs ~f:(fun (b : Block.t) -> b.x > 0) then *)
(*     Some (Set.map (module Block) bs ~f:(fun (b : Block.t) -> { b with x = b.x - 1 })) *)
(*   else None *)

(* (\* let rec zero bs = match shift_left bs with Some bs -> zero bs | None -> bs *\) *)

(* let motif_count ctx b b' = *)
(*   let rec rshift ct b' = *)
(*     let ct = ct + if Set.is_subset b' ~of_:b then 1 else 0 in *)
(*     match shift_right ctx b' with Some b' -> rshift ct b' | None -> ct *)
(*   in *)
(*   let rec ushift ct b' = *)
(*     let ct = rshift ct b' in *)
(*     match shift_up ctx b' with Some b' -> ushift ct b' | None -> ct *)
(*   in *)
(*   ushift 0 b' *)

(* let rec iter_shifts b f = *)
(*   f b; *)
(*   let b' = shift_down b in *)
(*   if not (Set.is_empty b') then iter_shifts b' f *)

(* (\* let blocks_distance_old s s' = *\) *)
(* (\*   let s = zero @@ Set.of_list (module Block) s in *\) *)
(* (\*   let s' = zero @@ Set.of_list (module Block) s' in *\) *)
(* (\*   let n = Float.of_int @@ Set.length (Set.inter s s') in *\) *)
(* (\*   let d = Float.of_int @@ Set.length (Set.union s s') in *\) *)
(* (\*   print_s [%message (n : float) (d : float)]; *\) *)
(* (\*   if Float.(d = 0.) then 0. else 1. -. (n /. d) *\) *)

(* (\* let blocks_distance s s' = *\) *)
(* (\*   [%test_result: float] ~expect:(blocks_distance_old s s') (blocks_distance s s'); *\) *)
(* (\*   blocks_distance s s' *\) *)

(* let rec zero bs = *)
(*   let min_x = *)
(*     Iter.of_set bs *)
(*     |> Iter.map (fun (b : Block.t) -> b.x) *)
(*     |> Iter.min |> Option.value ~default:0 *)
(*   in *)
(*   Set.map (module Block) bs ~f:(fun b -> { b with x = b.x - min_x }) *)
