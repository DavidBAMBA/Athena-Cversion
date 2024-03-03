#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "defs.h"
#include "athena.h"
#include "globals.h"
#include "string.h"
#include "prototypes.h"

static Real grav_pot2(const Real x1, const Real x2, const Real x3);
static Real hst_MagneticEnergyDensity(const GridS *pG, const int i, const int j, const int k);
static Real hst_ThermalEnergy(const GridS *pG, const int i, const int j, const int k);
static Real hst_Lorentz1(const GridS *pG, const int i, const int j, const int k);
static Real hst_Lorentz2(const GridS *pG, const int i, const int j, const int k);

static Real P_rho(const GridS *pG, const int i, const int j, const int k);
static Real magnetization(const GridS *pG, const int i, const int j, const int k);





/*------------------------------------------------------*/
/* Problem Setup */

void problem(DomainS *pDomain) {

  GridS *pGrid = (pDomain->Grid);		//Pointer to the grid
  
  //Grid Vars
  int i;
  int j;
  int k;
  int is = pGrid->is, ie = pGrid->ie;
  int js = pGrid->js, je = pGrid->je;
  int ks = pGrid->ks, ke = pGrid->ke;
  
  //Domain Size
  Real lx = pDomain->RootMaxX[0] - pDomain->RootMinX[0];
  Real ly = pDomain->RootMaxX[1] - pDomain->RootMinX[1];
  Real lz = pDomain->RootMaxX[2] - pDomain->RootMinX[2];
  
  //Initialize
  Real amp = par_getd("problem","amp");
  Real sigma = par_getd("problem","sigma");
  Real delta = par_getd("problem","delta");
  int nx = par_getd("problem","nx");
  int ny = par_getd("problem","ny");
  int nz = par_getd("problem","nz");
  Real x1;
  Real x2;
  Real x3;
  Real v1y;
  Real d0 = 1.0;
  Real b0 = sqrt(sigma*d0);		//b0 = B0/sqrt(4*PI)
  Real p0 = 0.5*b0*b0;			//d0 and p0 chosen so that sound speed = 1
  Real h0 = 3.0*d0 + Gamma*p0/Gamma_1;	//h0 = Enthalpy density in the hot layer

  for (k = ks; k <= ke; k++) {
    for (j = js; j <= je; j++) {
      for (i = is; i <= ie; i++) {
        cc_pos(pGrid,i,j,k,&x1,&x2,&x3);
        // Velocity perturbation in the z-direction ///////
      //  v1y = amp/4.0*(1.0+cos(2.0*PI*nx*x1/lx))*(1.0+cos(2.0*PI*ny*x2/ly));
      ////////////////////////////////////////////    
      //Zero net momentum
        v1y = amp*0.5*sin(2.0*PI*nx*x1/lx)*(1+cos(2.0*PI*ny*x2/ly));
      ///////////////////////////////////////////
  	pGrid->U[k][j][i].d = 3.0*d0;			//Let rho_0 = 1
  	pGrid->U[k][j][i].E = 3.0*d0+p0/Gamma_1;		//energy density w/o rest mass
  	pGrid->U[k][j][i].M1 = 0.0;
  	pGrid->U[k][j][i].M2 = 0.0;
	//Perturbation in velocity in the y-direction///////////
	pGrid->U[k][j][i].M2 = h0*v1y;
	/*----------------------------------------------------*/
	if (x2 <= -0.5*delta) {		//Lower B-field zone
	  pGrid->B3i[k][j][i] = b0;
	  if (i == ie) pGrid->B3i[k][j][ie+1] = b0;
	  pGrid->U[k][j][i].B3c = b0;
  	  pGrid->U[k][j][i].d = d0;			//Let rho_0 = 1
	  pGrid->U[k][j][i].E = d0+p0*(1+v1y*v1y);
	  pGrid->U[k][j][i].M2 = (d0+2*p0)*v1y;
	}
	if (x2 >= 0.5*delta) {		//Upper B-field zone
	  pGrid->B3i[k][j][i] = -b0;
	  if (i == ie) pGrid->B3i[k][j][ie+1] = -b0;
	  pGrid->U[k][j][i].B3c = -b0;
  	  pGrid->U[k][j][i].d = d0;			//Let rho_0 = 1
	  pGrid->U[k][j][i].E = d0+p0*(1+v1y*v1y);
	  pGrid->U[k][j][i].M2 = (d0+2*p0)*v1y;
	}
      }
    }
  }

/* Enroll gravitational potential to give acceleration in y-direction for 2D
 *  * Use special boundary condition routines.  In 2D, gravity is in the
 *   * y-direction, so special boundary conditions needed for x2
 *   */
  dump_history_enroll(hst_Lorentz1, "<Gam-p>");
  dump_history_enroll(hst_Lorentz2, "<Gam-C>");
  dump_history_enroll(hst_ThermalEnergy, "<Uth>");
  dump_history_enroll(hst_MagneticEnergyDensity, "<Ub>");

  StaticGravPot = grav_pot2;
  return;
}

/*==============================================================================
 * PROBLEM USER FUNCTIONS:
 * problem_write_restart() - writes problem-specific user data to restart files
 * problem_read_restart()  - reads problem-specific user data from restart files
 * get_usr_expr()          - sets pointer to expression for special output data
 * get_usr_out_fun()       - returns a user defined output function pointer
 * get_usr_par_prop()      - returns a user defined particle selection function
 * Userwork_in_loop        - problem specific work IN     main loop
 * Userwork_after_loop     - problem specific work AFTER  main loop
 *----------------------------------------------------------------------------*/

void problem_write_restart(MeshS *pM, FILE *fp)
{
  return;
}

/*
 * 'problem_read_restart' must enroll special boundary value functions,
 *    and initialize gravity on restarts
 */

void problem_read_restart(MeshS *pM, FILE *fp)
{
  int nl,nd;
  
  StaticGravPot = grav_pot2;
  return;
}

ConsFun_t get_usr_expr(const char *expr)
{
  if(strcmp(expr,"Bsqr")==0) return hst_MagneticEnergyDensity;
  if(strcmp(expr,"p_rho")==0) return P_rho;
  if(strcmp(expr,"mag")==0) return magnetization;
  return NULL;
}

VOutFun_t get_usr_out_fun(const char *name){
  return NULL;
}

void Userwork_in_loop(MeshS *pM)
{
}

void Userwork_after_loop(MeshS *pM)
{
}


/*=========================== PRIVATE FUNCTIONS ==============================*/

/*! \fn static Real grav_pot2(const Real x1, const Real x2, const Real x3)
 *  \brief Gravitational potential; g = 0.1
 */

static Real grav_pot2(const Real x1, const Real x2, const Real x3)
{
  return 0.01*x2;
}

static Real hst_Lorentz1(const GridS *pG, const int i, const int j, const int k)
{
  PrimS W;
  W = Cons_to_Prim (&(pG->U[k][j][i]));
  Real lorentz_factor = pG->U[k][j][i].d/W.d;

  return lorentz_factor;
}

static Real hst_Lorentz2(const GridS *pG, const int i, const int j, const int k)
{
  Real v1 = pG->U[k][j][i].M1/pG->U[k][j][i].d;
  Real v2 = pG->U[k][j][i].M2/pG->U[k][j][i].d;
  Real v3 = pG->U[k][j][i].M3/pG->U[k][j][i].d;
  Real v_squared = SQR(v1) + SQR(v2) + SQR(v3);
  Real g = 1.0 / sqrt( 1.0- v_squared );
  return g;
}

static Real hst_ThermalEnergy(const GridS *pG, const int i, const int j, const int k)
{
    PrimS W;
    W = Cons_to_Prim (&(pG->U[k][j][i]));
    Real U_th = 3*W.P;
    
    return U_th;
}

static Real hst_MagneticEnergyDensity(const GridS *pG, const int i, const int j, const int k)
{
    PrimS W;
    W = Cons_to_Prim (&(pG->U[k][j][i]));

    Real U_b =  SQR(W.B1c) + SQR(W.B2c) + SQR(W.B3c);

    return U_b;
}




static Real P_rho(const GridS *pG, const int i, const int j, const int k)
{
    PrimS W;
    W = Cons_to_Prim (&(pG->U[k][j][i]));

    Real pth =  W.P/W.d;

    return pth;
}


static Real magnetization(const GridS *pG, const int i, const int j, const int k)
{
    PrimS W;
    W = Cons_to_Prim (&(pG->U[k][j][i]));
    
    Real Bmag =  SQR(W.B1c) + SQR(W.B2c) + SQR(W.B3c);
    Real pth =  Bmag/W.d;

    return pth;
}



