#lang play
(require "T1.rkt")

(print-only-errors #t)

(test (occurrences (varp "x") "x") 1)
(test (occurrences (andp (varp "x") (varp "y")) "x") 1)
(test (occurrences (orp (varp "x") (varp "y")) "x") 1)
(test (occurrences (notp (orp (varp "x") (varp "y"))) "x") 1)
(test (occurrences (notp (andp (varp "x") (varp "x"))) "x") 2)

(test (vars (varp "x")) (list "x"))
(test (vars (andp (varp "x") (varp "y"))) (list "x" "y"))
(test (vars (orp (varp "x") (varp "x"))) (list "x"))
(test (vars (notp (orp (varp "x") (varp "y")))) (list "x" "y"))
(test (vars (andp (varp "x") (notp (varp "y")))) (list "x" "y"))

(test (all-environments '()) (list '()))
(test (all-environments (list "x"))
      (list (list (cons "x" #t)) (list (cons "x" #f))))
(test (all-environments (list "x" "y"))
      (list
       (list (cons "x" #t) (cons "y" #t))
       (list (cons "x" #t) (cons "y" #f))
       (list (cons "x" #f) (cons "y" #t))
       (list (cons "x" #f) (cons "y" #f))))
(test (all-environments (list "x" "y" "z"))
      (list
       (list (cons "x" #t) (cons "y" #t) (cons "z" #t))
       (list (cons "x" #t) (cons "y" #t) (cons "z" #f))
       (list (cons "x" #t) (cons "y" #f) (cons "z" #t))
       (list (cons "x" #t) (cons "y" #f) (cons "z" #f))
       (list (cons "x" #f) (cons "y" #t) (cons "z" #t))
       (list (cons "x" #f) (cons "y" #t) (cons "z" #f))
       (list (cons "x" #f) (cons "y" #f) (cons "z" #t))
       (list (cons "x" #f) (cons "y" #f) (cons "z" #f))))

(test (eval (varp "x") (list (cons "x" #t))) #t)
(test (eval (andp (varp "x") (varp "y")) (list (cons "x" #t) (cons "y" #f))) #f)
(test (eval (orp (varp "x") (varp "y")) (list (cons "x" #f) (cons "y" #t))) #t)
(test (eval (notp (varp "x")) (list (cons "x" #f))) #t)
(test (eval (andp (orp (varp "x") (varp "y")) (notp (varp "z"))) (list (cons "x" #t) (cons "y" #f) (cons "z" #t))) #f)
(test/exn (eval (varp "y") (list (cons "x" #t))) "Variable y is not defined in environment")

(test (tautology? (varp "x")) #f)
(test (tautology? (andp (varp "x") (notp (varp "x")))) #f)
(test (tautology? (orp (varp "x") (notp (varp "x")))) #t)
(test (tautology? (orp (andp (varp "x") (varp "y")) (orp (notp (varp "x")) (notp (varp "y"))))) #t)
(test (tautology? (orp (andp (varp "x") (varp "y")) (orp (notp (varp "x")) (varp "y")))) #f)

(test (simplify-negations (varp "x")) (varp "x"))
(test (simplify-negations (notp (varp "x"))) (notp (varp "x")))
(test (simplify-negations (notp (notp (varp "x")))) (varp "x"))
(test (simplify-negations (notp (andp (varp "x") (varp "y")))) (orp (notp (varp "x")) (notp (varp "y"))))
(test (simplify-negations (notp (orp (varp "x") (varp "y")))) (andp (notp (varp "x")) (notp (varp "y"))))

(test (distribute-and (varp "x")) (varp "x"))
(test (distribute-and (andp (orp (varp "x") (varp "y")) (varp "z"))) (orp (andp (varp "x") (varp "z")) (andp (varp "y") (varp "z"))))
(test (distribute-and (andp (varp "z") (orp (varp "x") (varp "y")))) (orp (andp (varp "z") (varp "x")) (andp (varp "z") (varp "y"))))
(test (distribute-and (andp (orp (varp "x") (varp "y")) (andp (varp "z") (varp "s"))))
      (orp (andp (varp "x") (andp (varp "z") (varp "s"))) (andp (varp "y") (andp (varp "z") (varp "s")))))
(test (distribute-and (andp (orp (notp(varp "x")) (notp(varp "y"))) (andp (varp "z") (varp "s"))))
      (orp (andp (notp(varp "x")) (andp (varp "z") (varp "s"))) (andp (notp(varp "y")) (andp (varp "z") (varp "s")))))

(test (( apply-until (\lambda (x) (/ x (add1 x))) (\lambda (x new-x) (<= (- x new-x) 0.1))) 1) 0.25)

(test (DNF (andp (orp (varp "a") (varp "b")) (orp (varp "c") (varp "d"))))
      (orp
       (orp (andp (varp "a") (varp "c"))
            (andp (varp "a") (varp "d")))
       (orp (andp (varp "b") (varp "c"))
            (andp (varp "b") (varp "d")))
       )
      )

(test (DNF (orp (andp (varp "a") (varp "b")) (varp "c")))
      (orp (andp (varp "a") (varp "b")) (varp "c")))