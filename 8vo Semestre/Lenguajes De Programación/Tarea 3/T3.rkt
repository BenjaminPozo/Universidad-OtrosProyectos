#lang play


#|
  Expr  ::= <num>
          | (+ <Expr> <Expr>)
          | (- <Expr> <Expr>)
          | (* <Expr> <Expr>)
          | <id>
          | (fun (<id> : <Type>) <Expr>)
          | (<Expr> <Expr>);
|#
(deftype Expr
  ;; core
  (num n)
  (binop op l r)
  ;; unary first-class functions
  (id x)
  (fun binder binderType body)
  (app callee arg)
  (ff)
  (tt)
  (ifc c t f)
  )

#| BEGIN P1 |#

#|
 <Type> ::= (numT)
            (arrowT <Type> <Type>)
            (boolT)
|#
(deftype Type
  (numT)
  (arrowT l r)
  (boolT)
 )

;; parse-type : s-expr -> Type
;; Transforma una expresión a su tipo de dato
(define (parse-type t)
  (match t
    ['Number (numT)]
    [(list '-> l r) (arrowT (parse-type l) (parse-type r))] 
    ['Boolean (boolT)]
    )
  )

;; parse : s-expr -> Expr
(define (parse s)
  (match s
    ['true (tt)]
    ['false (ff)]
    [n #:when (number? n) (num n)]
    [x #:when (symbol? x) (id x)]
    [(list '+ l r) (binop '+ (parse l) (parse r))]
    [(list '- l r) (binop '- (parse l) (parse r))]
    [(list '* l r) (binop '* (parse l) (parse r))]
    [(list '<= l r) (binop '<= (parse l) (parse r))]
    [(list 'if c t f) (ifc (parse c) (parse t) (parse f))]
    [(list 'fun (list binder ': type) body) (fun binder (parse-type type) (parse body))]
    [(list callee arg) (app (parse callee) (parse arg))]
    [_ (error 'parse "invalid syntax: ~a" s)]))

;; Implementación de ambientes de tipos
;; (análoga a la de ambientes de valores)

;; TypeEnv ::= ⋅ | <TypeEnv>, <id> : <Type>
(deftype TypeEnv (mtTenv) (aTenv id type env))
(define empty-tenv (mtTenv))
(define extend-tenv aTenv)

(define (tenv-lookup x env)
  (match env
    [(mtTenv) (error 'tenv-lookup "free identifier: ~a" id)]
    [(aTenv id type rest) (if (symbol=? id x) type (tenv-lookup x rest))]
    ))

;; infer-type : Expr Env -> Type
;; Toma una expresión y un ambiente e infiere el tipo de datos que retorna la expresión
(define (infer-type expr tenv)
  (match expr
    [(tt) (boolT)]
    [(ff) (boolT)]
    [(num n) (numT)]
    [(binop op l r)
     (match l
       [(num n)
        (match r
          [(num n)
           (match op
             ['<= (boolT)]
             [else (numT)]
             )
           ]
          [else (error 'infer-type "invalid operand type for ~a" op)])]
       [else (error 'infer-type "invalid operand type")]
       )]
    [(id x) (tenv-lookup x tenv)]
    [(fun binder binderType body)
     (define extended-env (extend-tenv binder binderType tenv))
     (arrowT binderType (infer-type body extended-env))
     ]
    [(app callee arg)
     (define funType (infer-type callee tenv))
     (match funType
       [(arrowT T1 T2)
        (if (equal? T1 (infer-type arg tenv))
            T2
            (error 'infer-type "function argument type mismatch"))]
       [else (error 'infer-type "function application to a non-function")])]
    [(ifc c t f)
     (define bool (infer-type c tenv))
     (match bool
       [(boolT)
        (if (equal? (infer-type t tenv) (infer-type f tenv))
            (infer-type f tenv)
            (error 'infer-type "if branches type mismatch"))]
       [else (error 'infer-type "if condition must be a boolean")]
       )
     ]
    ))


#| END P1 |#

#| BEGIN P2 PREAMBLE |#

;; ambiente de sustitución diferida
(deftype Env
  (mtEnv)
  (aEnv id val env))

;; interface ADT (abstract data type) del ambiente
(define empty-env (mtEnv))

;; "Simplemente" asigna un nuevo identificador para aEnv
;(define extend-env aEnv)
;;
;; es lo mismo que definir extend-env así:
;; (concepto técnico 'eta expansion')
(define (extend-env id val env) (aEnv id val env))

(define (env-lookup x env)
  (match env
    [(mtEnv) (error 'env-lookup "free identifier: ~a" x)]
    [(aEnv id val rest) (if (symbol=? id x) val (env-lookup x rest))]))

;; num2num-op : (Number Number -> Number) -> Val Val -> Val
(define (num2num-op op)
  (λ (l r)
    (match (cons l r)
      [(cons (num n) (num m)) (num (op n m))]
      [_ (error 'num-op "invalid operands")])))


(define num+ (num2num-op +))
(define num- (num2num-op -))
(define num* (num2num-op *))

#| END P2 PREAMBLE |#

#| BEGIN P2 |#

;; final? : Expr -> Boolean
;; Toma una expresión y retorna un booleano dependiendo de si la expresión es un valor o no
(define (final? e)
  (match e
    [(num _) #t]
    [(fun _ _ _) #t]
    [else #f]
    )
  )

(deftype Kont
  (mt-k)
  (binop-r-k op comp env ref)
  (binop-l-k op comp env ref)
  (arg-k arg env ref)
  (fun-k fun env ref)
  )

(define empty-kont (mt-k))

;; State ::= (<Expr>, <Env>, <Kont>)
(deftype State
  (st expr env kont)
  )

;; inject : Expr -> State
;; Recibe una expresión y crea un estado inicial
(define (inject expr)
  (st expr mtEnv empty-kont)
  )

;; step : State -> State
;; Toma un estado y produce uno nuevo
(define (step c)
  (match c
    [(st expr env kont)
     (match expr
       [(binop op l r) (st l env (binop-r-k op r env kont))]
       [(id x) (define pair (env-lookup x env))
               (st (car pair) (cdr pair) kont)]
       [(app callee arg) (st callee env (arg-k arg env kont))]
       [else
        (match kont
          [(binop-r-k op comp benv k) (st comp benv (binop-l-k op expr env k))]
          [(binop-l-k op comp benv k)
           (match op
             ['+ (st (num+ expr comp) env k)]
             ['- (st (num- expr comp) env k)]
             ['* (st (num* expr comp) env k)]
             )
           ]
          [(arg-k arg aenv k) (st arg aenv (fun-k expr env k))]
          [(fun-k (fun binder binderType body) fenv k)
           (define extended-env (extend-env binder (cons expr env) fenv))
           (st body extended-env k)])])]))

;; eval : Expr -> Expr
(define (eval expr)
  (define (eval-until-final state)
    (def (st expr _ kont) state)
    (if (and (final? expr) (mt-k? kont))
        expr
        (eval-until-final (step state))))
  (eval-until-final (inject expr)))

;; run : s-expr -> Expr Type
;; Toma una expresión s-expr y retorna una expresión con su tipo
(define (run s-expr)
  (define parsed-expr (parse s-expr))
  (define eval-expr (eval parsed-expr))
  (define type-expr (infer-type eval-expr mtEnv))
  (cons eval-expr type-expr)
  )
