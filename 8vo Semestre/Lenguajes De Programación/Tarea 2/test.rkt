#lang play
(require "T2.rkt")

(print-only-errors #t)

;; test 1a

(test (parse true) (tt))
(test (parse false) (ff))
(test (parse '(<= 10 14)) (leq (num 10) (num 14)))
(test (parse ' ( if (<= 30 50) 20 40)) ( ifc (leq (num 30) (num 50)) (num 20) (num 40)))

;; test 1b

(test (parse 'a) (id 'a))
(test (parse 'abc) (id 'abc))
(test (parse ' (fun (left right) (* left right))) (fun ( list 'left 'right) (mul (id 'left) (id 'right))))
(test (parse ' (fun (left right) (+ left right))) (fun ( list 'left 'right) (add (id 'left) (id 'right))))
(test (parse ' (fun (left right) (- left right))) (fun ( list 'left 'right) (sub (id 'left) (id 'right))))
(test (parse ' (fun (left right) (<= left right))) (fun ( list 'left 'right) (leq (id 'left) (id 'right))))
(test  (parse '(f 20 30 40)) (app (id 'f) (list (num 20) (num 30) (num 40))))
(test  (parse '(f 20)) (app (id 'f) (list (num 20))))
(test  (parse '(f 20 20 20 20 20 20 20 20)) (app (id 'f) (list (num 20) (num 20) (num 20) (num 20) (num 20) (num 20) (num 20) (num 20))))

;; test 1d

(test (num+ (numV 3) (numV 4)) (numV 7))
(test (num+ (numV 3) (numV -4)) (numV -1))
(test (num- (numV 3) (numV 4)) (numV -1))
(test (num- (numV 3) (numV -4)) (numV 7))
(test (num* (numV 3) (numV 4)) (numV 12))
(test (num* (numV 3) (numV -4)) (numV -12))
(test/exn (num+ (numV 4) (boolV #t)) "num-op: invalid operands")
(test (num<= (numV 3) (numV 4)) (boolV #t))
(test (num<= (numV 4) (numV 3)) (boolV #f))

;; test 1e

(test (eval (parse '(+ 3 4)) empty-env) (numV 7))
(test (eval (parse '(+ 3 -4)) empty-env) (numV -1))
(test (eval (parse '(- 3 4)) empty-env) (numV -1))
(test (eval (parse '(- 3 -4)) empty-env) (numV 7))
(test (eval (parse '(* 3 4)) empty-env) (numV 12))
(test (eval (parse '(* 3 -4)) empty-env) (numV -12))
(test (eval (parse '(<= 3 4)) empty-env) (boolV #t))
(test (eval (parse '(<= 4 3)) empty-env) (boolV #f))
(test (eval (parse '(if (<= 3 4) (+ 1 2) (* 2 3))) empty-env) (numV 3))
(test (eval (parse '(if (<= 4 3) (+ 1 2) (* 2 3))) empty-env) (numV 6))
(test (eval (parse '(fun (x y) (+ x y))) empty-env) (closureV (list 'x 'y) (add (id 'x) (id 'y)) empty-env)) 
(test (eval (parse '(fun (x y) (- x y))) empty-env) (closureV (list 'x 'y) (sub (id 'x) (id 'y)) empty-env)) 
(test (eval (parse '(fun (x y) (* x y))) empty-env) (closureV (list 'x 'y) (mul (id 'x) (id 'y)) empty-env)) 
(test (eval (parse '(fun (x y) (<= x y))) empty-env) (closureV (list 'x 'y) (leq (id 'x) (id 'y)) empty-env))
(test (eval (app (id 'my-fun) (list (num 1) (num 2) (num 3))) (aEnv 'my-fun (closureV (list 'x 'y 'z)  (parse '(* z (+ x y))) (mtEnv)) (mtEnv))) (numV 9))

;; test 1f

(test (parse '(tuple 10 20 30)) (tupl (list (num 10) (num 20) (num 30))))
(test (parse '(tuple 10 20 30 10 20 30 10 20 30)) (tupl (list (num 10) (num 20) (num 30) (num 10) (num 20) (num 30) (num 10) (num 20) (num 30))))
(test (parse ' (proj (tuple 10 20 30) 1)) (proj (tupl (list (num 10) (num 20) (num 30))) (num 1)))

;; test 1g
