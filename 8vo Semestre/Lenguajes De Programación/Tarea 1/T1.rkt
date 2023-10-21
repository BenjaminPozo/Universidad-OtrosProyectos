#lang play

#| P1 |#

#| Parte A |#
#|
<Prop> ::= (varp <string>)
        |  (andp <Prop> <Prop>)
        |  (orp <Prop> <Prop>)
        |  (notp <Prop>)
|#

(deftype Prop
  (varp name)
  (andp p q)
  (orp p q)
  (notp p))

#| Parte B |#

;; occurrences :: Prop String -> Number
;; Calcula la cantidad de veces que aparece una variable en una proposición
(define (occurrences prop string)
  (match prop
    [(varp name) (if (equal? name string) 1 0)]
    [(andp p q) (+ (occurrences p string) (occurrences q string))]
    [(orp p q) (+ (occurrences p string) (occurrences q string))]
    [(notp p) (occurrences p string)]))

#| Parte C |#

;; vars :: Prop -> (Listof String)
;; Recibe una proposición y devuelve una lista con todas las variables sin repetirse
(define (vars prop)
  (match prop
    [(varp name) (cons name '())]
    [(andp p q) (remove-duplicates (append (vars p) (vars q)))]
    [(orp p q)  (remove-duplicates (append (vars p) (vars q)))]
    [(notp p) (vars p)]))

#| Parte D |#

;; all-environments :: (Listof String) -> (Listof (Listof (Pair String Boolean)))
;; Se le da una lista de variables y devuelve la combinación de verdadero y falso de todas las variables en pares ordenados,
;;  dentro listde una lista que esta en otra lista
(define (all-environments variables)
  (if (null? variables)
      (list '())
      (let ((sub-environment (all-environments (cdr variables))))
        (append
         (map
          (lambda (env)
            (cons (cons (car variables) #t) env)) sub-environment)
         (map
          (lambda (env)
            (cons (cons (car variables) #f) env)) sub-environment)))))

#| Parte E |#

;; eval :: Prop (Listof (Pair String Boolean)) -> Boolean
;; Recibe una proposición y un ambiente y evalua la proposición con los
;; valores del env para dar un resultado
(define (eval prop var)
  (match prop
    [(varp name)
     (let ((value (assoc name var)))
       (if value
           (cdr value)
           (error 'lookup "Variable ~a is not defined in environment" name)))]
    [(andp p q)
     (let ((bool1 (eval p var)))
       (let ((bool2 (eval q var)))
         (and bool1 bool2)))]
    [(orp p q)
     (let ((bool1 (eval p var)))
       (let ((bool2 (eval q var)))
         (or bool1 bool2)))]
    [(notp p) (not (eval p var))]))

#| Parte F |#

;; tautology? :: Prop -> Boolean
;; Función que verifica si una proposición es una tautología
(define (tautology? prop)
  (define all-vars (vars prop))
  (define all-envs (all-environments all-vars))
  (define resp (map (lambda (env) (eval prop env)) all-envs))
  (define (loop boolean-list)
    (cond
      [(equal? '() boolean-list) #t]
      [(equal? #f (car boolean-list)) #f]
      [else (loop (cdr boolean-list))]
      )
  )
  (loop resp)
  )

#| P2 |#

#| Parte A |#

;; simplify-negations :: Prop -> Prop
;; Esta función simplifica los notp de una proposición
(define (simplify-negations prop)
  (match prop
    [(varp name) prop]
    [(andp p q) (andp (simplify-negations p) (simplify-negations q))]
    [(orp p q) (orp (simplify-negations p) (simplify-negations q))]
    [(notp p)
     (match p
       [(varp name2) prop]
       [(andp p2 q2) (orp (notp p2) (notp q2))]
       [(orp p2 q2) (andp (notp p2) (notp q2))]
       [(notp p2) p2])]))

#| Parte B |#

;; distribute-and :: Prop -> Prop
;; Función que distribuye los and de las proposiciones respecto a los or
;; (andp (varp p) (orp (p2) (q2)))
(define (distribute-and prop)
  (match prop
    [(varp name) prop]
    [(andp p q)
     (match p
       [(orp p2 q2) (orp (andp (distribute-and p2) q) (andp (distribute-and q2) q))]
       [else
        (match q
          [(orp p2 q2) (orp (andp p (distribute-and p2)) (andp p (distribute-and q2)))]
          [else (andp (distribute-and p) (distribute-and q))])])]
    [(orp p q) (orp (distribute-and p) (distribute-and q))]
    [(notp p) (notp (distribute-and p))]))

#| Parte C |#

;; apply-until :: (a -> a) (a a -> Boolean) -> a -> a
;; Función que aplica otra función hasta que se cumpla un predicado
(define (apply-until fx pr)
  (λ (x)
    (define (loop fn prd x)
    (let ((new-x (fn x)))
      (if (equal? #t (prd x new-x))
          new-x (loop fn prd new-x))
      )
    )
  (loop fx pr x))
  )

#| Parte D |#

;; DNF :: Prop -> Prop
(define (DNF prop)
  (let
      ((smp-not
        ((apply-until simplify-negations (\lambda (x new-x) (equal? x new-x))) prop)))
    ((apply-until distribute-and (\lambda (x new-x) (equal? x new-x))) smp-not)
    )
  )

#| P3 |#

#| Parte A |#

;; fold-prop :: (String -> a) (a a -> a) (a a -> a) (a -> a) -> Prop -> a

#| Parte B |#

;; occurrences-2 :: Prop String -> Number

;; vars-2 :: Prop -> (Listof String)

;; eval-2 :: Prop (Listof (Pair String Boolean)) -> Boolean

;; simplify-negations-2 :: Prop -> Prop

;; distribute-and-2 :: Prop -> Prop
