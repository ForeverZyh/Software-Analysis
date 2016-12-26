void doit(Fun *f)
{
	Ins *Entry=f->getEntry();
	for(Ins*i=Entry;i=i->next_Ins())
	{
		if (i->type=="for")
		{
			Ins *inner=i->inner_Ins();
			modify.clear();
			use.clear();
			bool flag=1;
			for(Ins*j=inner;j;j->next_Ins())
			{
				for(Var *x in j)
				{
					if (x->isPrimVar&&x->isModify&&!x->isReduction)
					{
						flag=0;break;
					}
					if (!x->isPrimVar)
					{
						if (x->isUse) use.add(x);
						if (x->isModify) modify.add(x);
					}
				}
				if (!flag) break;
			}
			if (flag)
			{
				if (isIntersec(use,modify))
				{
					printf("Can't: Need further analysis.\n");
					for(Var *x in use)
						for(Var *y in use)
							if (x->Ref==y->Ref)
							{
								printf("assert: ");
								x->print();//the expression in x i->@i1
								y->print();//the expression in y i->@12
								printf("\n");
							}
					printf("if SAT : can't parallel\nif UNSAT : can parallel\n");
				}
				else printf("Can: Parallel!\n");
			}
			else 
			{
				printf("Can't: Var %s can not or may not be reduction.\n",hfh->name());
			}
		}
	}
}
