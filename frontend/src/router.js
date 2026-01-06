import { userResource } from "@/data/user"
import { createRouter, createWebHistory } from "vue-router"
import { session } from "./data/session"

const routes = [
	{
		path: "/",
		name: "Home",
		component: () => import("@/pages/Index.vue"),
	},
	{
		path: "/gantt",
		name: "GanttChart",
		component: () => import("@/components/GanttChart.vue"),
	},
	{
		path: "/forecast-history",
		name: "ForecastHistory",
		component: () => import("@/pages/ForecastHistory.vue"),
	},
	{
		path: "/dashboard",
		name: "Dashboard",
		component: () => import("@/pages/Dashboard.vue"),
	},
	{
		name: "Login",
		path: "/account/login",
		component: () => import("@/pages/Login.vue"),
	},
	{
		name: "Index",
		path: "/app",
		component: () => import("@/pages/Index.vue"),
	},
]

const router = createRouter({
	history: createWebHistory("/frontend"),
	routes,
})

router.beforeEach(async (to, from, next) => {
	let isLoggedIn = session.isLoggedIn
	try {
		await userResource.promise
	} catch (error) {
		isLoggedIn = false
	}

	if (to.name === "Login" && isLoggedIn) {
		next({ name: "Home" })
	} else if (to.name !== "Login" && !isLoggedIn) {
		next({ name: "Login" })
	} else {
		next()
	}
})

export default router
