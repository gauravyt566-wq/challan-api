export default {
async fetch(request) {
const DEVELOPER = "@ZephrexXx";
// Headers
const headers = {
"Content-Type": "application/json; charset=utf-8",
"Access-Control-Allow-Origin": "*"
};
// URL & params
const url = new URL(request.url);
const vehicleParam = url.searchParams.get("vehicle");
// 🔹 Input check
if (!vehicleParam) {
return new Response(
JSON.stringify({
success: false,
error: "Vehicle number required",
developer: DEVELOPER
}),
{ status: 400, headers }
);
}
const vehicle = vehicleParam.trim().toUpperCase();
if (vehicle.length < 6) {
return new Response(
JSON.stringify({
success: false,
error: "Invalid vehicle number",
provided: vehicle,
developer: DEVELOPER
}),
{ status: 400, headers }
);
}
// 🌐 External API
const apiUrl =
"https://api-ij32.onrender.com/vehicle?text=" +
encodeURIComponent(vehicle);
try {
const apiResponse = await fetch(apiUrl, {
headers: {
"User-Agent": "Mozilla/5.0 (ZephrexXx API)"
}
});
const data = await apiResponse.json();
// 🔹 Extract ONLY challans
let challans = [];
if (data && Array.isArray(data.challans)) {
challans = data.challans;
}
// ✅ FINAL CLEAN RESPONSE
return new Response(
JSON.stringify(
{
success: true,
vehicle: vehicle,
challans: challans,
developer: DEVELOPER
},
null,
2
),
{ status: 200, headers }
);
} catch (err) {
return new Response(
JSON.stringify({
success: false,
error: "Failed to fetch data",
developer: DEVELOPER
}),
{ status: 500, headers }
);
}
}
};
