#lang play
(print-only-errors)

;; PARTE 1A, 1B, 1F

#|
  <Expr> ::= (num <number>)
           | (add <Expr> <Expr>)
           | (sub <Expr> <Expr>)
           | (mul <Expr> <Expr>)
           | (tt)
           | (ff)
           | (leq <Expr> <Expr>)
           | (ifc <Expr> <Expr> <Expr>)
           | (id <Symbol>)
           | (fun <list <Symbol>> <Expr>)
           | (app <Symbol> <list <number>>)
           | (tupl <list <Expr>>)
           | (proj <Expr> <Expr>)
|#
(deftype Expr
  ;; core
  (num n)
  (add l r)
  (sub l r)
  (mul l r)
  (tt)
  (ff)
  (leq lexpr rexpr)
  (ifc c expr1 expr2)
  (id x)
  (fun arg body)
  (app f-name f-args)
  (tupl t)
  (proj tup e)
  )

;; parse :: s-expr -> Expr
;; Transforma una expresión ...
(define (parse s-expr)
  (match s-expr
    [n #:when (number? n) (num n)] 
    [(list '+ l r) (add (parse l) (parse r))]
    [(list '- l r) (sub (parse l) (parse r))]
    [(list '* l r) (mul (parse l) (parse r))]
    [#t (tt)]
    [#f (ff)]
    [(list '<= l r) (leq (parse l) (parse r))]
    [(list 'if c l r) (ifc (parse c) (parse l) (parse r))]
    [x #:when (symbol? x) (id x)]
    [(list 'fun x b) (fun x (parse b))]
    [(list t elems ...) #:when (equal? t 'tuple) (tupl (map parse elems))]
    [(list p t e) #:when (equal? p 'proj) (proj (parse t) (parse e))]
    [(list f elems ...) (app (parse f) (map parse elems))]
    )
  )

;; PARTE 1C, 1G

#|
  Val ::= (numV <number>)
           | (boolV <bool>)
           | (tupleV <list <Val>>)
           | (projV <Val> <Val>)
           | (clousureV <Symbol> <Expr> <Env>)
|#

(deftype Val
  (numV n)
  (boolV b)
  (tupleV t)
  (projV t v)
  (closureV id body env)
  )

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

;; PARTE 1D

;; num2num-op :: Symbol -> (Val Val -> Val)
;; Toma un simbolo de que represente una operación y devuelve una funcion que
;; calcula la operacion de 2 estructuras Val
(define (num2num-op o)
  (define (fn x y)
        (match x
          [(numV n)
           (if (number? n)
               (match y
                 [(numV m)
                  (if (number? m)
                      (match o
                        [+ (numV (+ n m))]
                        [- (numV (- n m))]
                        [* (numV (* n m))]
                        )
                      (error "num-op: invalid operands")
                      )
                  ]
                 [else (error "num-op: invalid operands")])
               (error "num-op: invalid operands")
               )
           ]
          [else (error "num-op: invalid operands")]))
      fn
  )

(define num+ (num2num-op +))
(define num- (num2num-op -))
(define num* (num2num-op *))

;; num2bool-op :: Symbol -> (Val Val -> Val)
;; Recibe un simbolo que represente una condicion y devuelve una funcion que
;; toma dos valores de estructura Val y evalua la condicion en ellos.
(define (num2bool-op o)
  (define (fn x y)
        (match x
          [(numV n)
           (if (number? n)
               (match y
                 [(numV m)
                  (if (number? m)
                      (match o
                        [<= (boolV (<= n m))]
                        )
                      (error "num-op: invalid operands")
                      )
                  ]
                 [else (error "num-op: invalid operands")])
               (error "num-op: invalid operands")
               )
           ]
          [else (error "num-op: invalid operands")]))
      fn
  )

(define num<= (num2bool-op <=))


;; PARTE 1E, 1G

;; eval :: Expr Env -> Val
;; Evalua una estructura de expresión en un ambiente y devuelve la respuesta
;; del caso evaluado en una estructura tipo Val
(define (eval expr env)
  (match expr
    [(num n) (numV n)]
    [(id x) (env-lookup x env)]
    [(fun arg body) (closureV arg body env)]
    [(add l r) (num+ (eval l env) (eval r env))]
    [(sub l r) (num- (eval l env) (eval r env))]
    [(mul l r) (num* (eval l env) (eval r env))]
    [(leq l r) (num<= (eval l env) (eval r env))]
    [(ifc c l r) (if (equal? (boolV #t) (eval c env))
                     (eval l env)
                     (eval r env)
                     )]
    [(app f e) (def (closureV the-arg the-body the-claus-env) (eval f env))
               (eval the-body
                     (foldl (λ (args arg-expr new-env)
                              (extend-env args (eval arg-expr env) new-env))
                            empty-env
                            the-arg
                            e
                            ))]
    [(tupl t)
     (define eval-elems
       (map (λ (x) (eval x env)) t))
     (tupleV eval-elems)]
    
    [(proj t v)
     (def i v)
     (define iesimo (list-ref (eval t env) i))
     (projV (eval iesimo env))
     ]
    )
  )


;; PARTE 2A

(define swap* '???)
(define curry* '???)
(define uncurry* '???)
(define partial* '???)

;; PARTE 2B

;; run :: ...
(define (run) '???)
