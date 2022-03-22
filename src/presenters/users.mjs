import { Endpoints } from "./endpoints.mjs";

/**
 * @classdesc User
 */
export class User {
    /**
     * @param {!number} username - User identifier
     * @param {?string} email - Email address
     * @param {!string} updated - Updated date time (ISO 8601)
     */
    constructor(username, email, updatedAt) {
        this.username = username;
        this.email = email;
        this.updatedAt = new Date(updatedAt);
    }
}

/**
 * /api/v1/users
 * @module getUsers
 * @param {number} offset - Offset
 * @param {number} limit - Limit
 * @return {Array<User>} - Array of user
 */
export async function getUsers(offset = 0, limit = null) {
    const users = [];
    let url = `${Endpoints.USERS_URL}?offset=${offset}`;

    if (limit !== null) {
        url += `&limit=${limit}`
    }

    const response = await fetch(encodeURI(url), {
        mode: "cors",
        method: "GET",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        }
    });

    if (response.ok) {
        for (const user of await response.json()) {
            users.push(new User(user.username, user.email, user.updated_at));
        }
    } else {
        throw new Error(response.statusText);
    }

    return users;
}